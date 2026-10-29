#!/usr/bin/env python3
"""Validate archive data and local references using only the Python standard library."""
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class ResourceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if value is not None and key in ('src', 'href'):
                self.references.append((tag, key, value))


def markdown_targets(text):
    """Read balanced link destinations; PDF filenames legitimately contain ()."""
    position = 0
    while True:
        start = text.find('](', position)
        if start < 0:
            return
        depth, end = 1, start + 2
        while end < len(text) and depth:
            if text[end] == '(' and (end == 0 or text[end - 1] != '\\'):
                depth += 1
            elif text[end] == ')' and (end == 0 or text[end - 1] != '\\'):
                depth -= 1
            end += 1
        if depth:
            return
        yield text[start + 2:end - 1].strip().strip('<>')
        position = end


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    errors, warnings = [], []
    checks = 0

    def require(condition, message):
        nonlocal checks
        checks += 1
        if not condition:
            errors.append(message)

    def local_path(value, base=root):
        path = (base / unquote(urlsplit(value).path)).resolve()
        require(path.is_relative_to(root), f'Path escapes archive: {value}')
        require(path.is_file(), f'Missing local file: {value}')
        return path

    def load(path):
        try:
            return json.loads(path.read_text(encoding='utf-8-sig'))
        except (OSError, ValueError) as exc:
            errors.append(f'{path.name}: {exc}')
            return {}

    payload = load(root / 'data/lessons.json')
    concepts_data = load(root / 'data/concepts.json')
    lessons = payload.get('lessons', [])
    concepts = concepts_data.get('concepts', [])
    require(bool(lessons), 'No lessons imported')
    require(bool(concepts), 'No concepts imported')
    lesson_map = {x.get('id'): x for x in lessons}
    concept_map = {x.get('id'): x for x in concepts}
    require(len(lesson_map) == len(lessons), 'Duplicate lesson IDs')
    require(len(concept_map) == len(concepts), 'Duplicate concept IDs')
    source_maps, transcripts = {}, {}
    allowed_types = {'teacher_quote', 'transcript_summary', 'ai_analysis', 'personal_record'}
    required_sections = {'outline', 'explanations', 'examples', 'examTips', 'personalNotes', 'connections'}
    for lesson in lessons:
        lid = lesson.get('id', '')
        require(bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', lid)), f'{lid}: unstable date ID')
        require(lesson.get('date') == lid, f'{lid}: date differs from ID')
        sources = lesson.get('sources', [])
        smap = {s.get('id'): s for s in sources}
        source_maps[lid] = smap
        require(len(smap) == len(sources), f'{lid}: duplicate source IDs')
        for source in sources:
            path = source.get('path')
            if path:
                require(not urlsplit(path).scheme, f'{lid}: source must be a local copy: {path}')
                local_path(path)
            else:
                require(source.get('kind') == 'personal', f'{lid}: only chat personal records may have a null path')
        tpath = lesson.get('transcriptPath')
        require(bool(tpath), f'{lid}: no transcriptPath')
        transcript = load(local_path(tpath)) if tpath else {}
        require(transcript.get('lessonId') == lid, f'{lid}: transcript lessonId mismatch')
        blocks = transcript.get('blocks', [])
        require(bool(blocks), f'{lid}: transcript has no blocks')
        timestamps = {b.get('timestamp') for b in blocks}
        block_ids = [b.get('id') for b in blocks]
        require(len(set(block_ids)) == len(block_ids), f'{lid}: duplicate transcript block IDs')
        seconds = []
        for block in blocks:
            stamp = block.get('timestamp', '')
            valid = bool(re.fullmatch(r'\d{2}:\d{2}:\d{2}', stamp))
            require(valid, f'{lid}: invalid timestamp {stamp}')
            if valid:
                h, m, s = map(int, stamp.split(':'))
                require(m < 60 and s < 60, f'{lid}: invalid clock fields: {stamp}')
                seconds.append(h * 3600 + m * 60 + s)
        require(seconds == sorted(seconds), f'{lid}: unordered transcript timestamps')
        if blocks:
            require(lesson.get('recording', {}).get('lastTimestamp') == blocks[-1].get('timestamp'), f'{lid}: last timestamp mismatch')
        transcripts[lid] = {'timestamps': timestamps, 'blocks': blocks}
        require(required_sections <= set(lesson.get('sections', {})), f'{lid}: missing sections (use [] for missing evidence)')
        card_ids = []
        for name, cards in lesson.get('sections', {}).items():
            require(isinstance(cards, list), f'{lid}/{name}: section must be an array')
            if not isinstance(cards, list):
                continue
            for card in cards:
                card_ids.append(card.get('id'))
                require(card.get('sourceType') in allowed_types, f'{lid}/{card.get("id")}: unknown sourceType')
                require(bool(card.get('sources')), f'{lid}/{card.get("id")}: evidence is missing')
                if card.get('sourceType') == 'teacher_quote':
                    normalized_quote = re.sub(r'\s+', '', card.get('text', ''))
                    original = ''.join(re.sub(r'\s+', '', b.get('text', '')) for b in blocks)
                    require(bool(normalized_quote) and normalized_quote in original, f'{lid}/{card.get("id")}: teacher quote is not verbatim in transcript')
        require(len(card_ids) == len(set(card_ids)), f'{lid}: duplicate card IDs')
        for cid in lesson.get('conceptIds', []):
            require(cid in concept_map, f'{lid}: unknown concept {cid}')
            if cid in concept_map:
                require(lid in concept_map[cid].get('lessonIds', []), f'{lid}/{cid}: missing concept-to-lesson backlink')

    def check_reference(ref, lid, context):
        require(lid in lesson_map, f'{context}: unknown lesson {lid}')
        smap = source_maps.get(lid, {})
        source_id = ref.get('sourceId')
        require(source_id in smap, f'{context}: unknown sourceId {source_id}')
        source = smap.get(source_id, {})
        timestamp = ref.get('timestamp')
        if timestamp:
            require(timestamp in transcripts.get(lid, {}).get('timestamps', set()), f'{context}: missing source timestamp {timestamp}')
            require(source.get('kind') == 'transcript', f'{context}: timestamp must cite a transcript source')
        page = ref.get('page')
        if page is not None:
            require(isinstance(page, int) and page > 0, f'{context}: invalid PDF page {page}')
            require(source.get('kind') == 'courseware', f'{context}: page citation must cite courseware')
            count = source.get('pageCount')
            if isinstance(page, int) and isinstance(count, int):
                require(page <= count, f'{context}: page {page} exceeds {count}')
            elif source.get('kind') == 'courseware':
                warnings.append(f'{context}: no pageCount metadata; only positive page number checked')

    for lid, lesson in lesson_map.items():
        for name, cards in lesson.get('sections', {}).items():
            for card in cards:
                for ref in card.get('sources', []):
                    check_reference(ref, lid, f'{lid}/{name}/{card.get("id")}')
    for cid, concept in concept_map.items():
        for lid in concept.get('lessonIds', []):
            require(lid in lesson_map, f'{cid}: unknown lesson backlink {lid}')
            if lid in lesson_map:
                require(cid in lesson_map[lid].get('conceptIds', []), f'{cid}/{lid}: missing lesson-to-concept backlink')
        for relation in concept.get('relations', []):
            require(relation.get('targetId') in concept_map, f'{cid}: unknown relation target')
            require(relation.get('type') in {'classroom', 'analysis'}, f'{cid}: invalid relation type')
            require(bool(relation.get('sources')), f'{cid}: relation has no evidence')
            for ref in relation.get('sources', []):
                check_reference(ref, ref.get('lessonId'), f'{cid}/relation')

    for path in root.rglob('*.html'):
        html = ResourceParser()
        html.feed(path.read_text(encoding='utf-8'))
        for tag, key, value in html.references:
            require(value not in {'', '#'}, f'{path.name}: empty/placeholder {key}')
            require('example.com' not in value and 'YOUR-' not in value, f'{path.name}: placeholder URL')
            parsed = urlsplit(value)
            if not parsed.scheme and parsed.path:
                local_path(value, path.parent)
    for path in root.rglob('*.css'):
        for value in re.findall(r'url\([\s\'\"]*([^\)\'\"]+)', path.read_text(encoding='utf-8')):
            if not urlsplit(value).scheme and not value.startswith('#'):
                local_path(value, path.parent)
    for path in root.rglob('*.md'):
        for value in markdown_targets(path.read_text(encoding='utf-8-sig')):
            parsed = urlsplit(value)
            require(value not in {'', '#'}, f'{path.name}: placeholder Markdown link')
            if parsed.scheme:
                require(parsed.scheme in {'http', 'https', 'mailto'}, f'{path.name}: nonportable local Markdown link: {value}')
            elif parsed.path:
                local_path(value, path.parent)

    print(f'Validated {len(lessons)} lessons, {len(concepts)} concepts, {sum(len(t["blocks"]) for t in transcripts.values())} transcript paragraphs; {checks} checks.')
    for message in sorted(set(warnings)):
        print('WARNING:', message)
    for message in errors:
        print('ERROR:', message)
    print('PASS' if not errors else f'FAIL: {len(errors)} error(s)')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
