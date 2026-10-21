"""
study-map v0.1 —— 用数据结构管理你的学习数据
================================================
数据结构：列表（list）+ 字典（dict）
- 所有课程放在一个 list 里 → 这是"线性表"
- 每门课是一个 dict → 这是"键值对/哈希表"的思想

用法：
    python3 study_map.py              # 查看全部课程
    python3 study_map.py --todo        # 查看所有待办任务（按截止时间排序）
    python3 study_map.py --priority    # 按优先级排序
    python3 study_map.py --course <id> # 查看某一门课的详情
"""

import json
import sys
from datetime import datetime


def load_data():
    """读取课程数据——从 JSON 文件加载到 Python 的 list + dict 里"""
    with open('data/courses.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['courses']


def show_all(courses):
    """展示全部课程概览"""
    print("=" * 60)
    print(f"📚 学习地图 · 共 {len(courses)} 门课")
    print("=" * 60)

    # 按优先级从高到低排
    sorted_courses = sorted(courses, key=lambda c: c['priority'], reverse=True)

    for i, c in enumerate(sorted_courses, 1):
        stars = "⭐" * c['priority']
        undone = sum(1 for t in c['tasks'] if not t['done'])
        print(f"\n{i}. 【{c['name']}】 {stars}")
        print(f"   状态：{c['status']}  |  当前进度：{c['chapter']}")
        print(f"   待办：{undone} 件")
        # 最近的一个 deadline
        undone_tasks = [t for t in c['tasks'] if not t['done']]
        if undone_tasks:
            nearest = min(undone_tasks, key=lambda t: t['deadline'] if t['deadline'] != '待定' and t['deadline'] != '长期' and t['deadline'] != '多个' else '9999-99-99')
            print(f"   最近截止：{nearest['deadline']} — {nearest['name']}")


def show_todo(courses):
    """展示所有待办任务，按截止时间排序"""
    all_tasks = []
    for c in courses:
        for t in c['tasks']:
            if not t['done']:
                all_tasks.append({
                    'course': c['name'],
                    'task': t['name'],
                    'deadline': t['deadline'],
                    'priority': c['priority']
                })

    # 排序：能排日期的排前面，"待定"/"长期"/"多个"放最后
    def sort_key(t):
        d = t['deadline']
        if d in ('待定', '长期', '多个'):
            return (1, '9999-99-99')
        return (0, d)

    all_tasks.sort(key=sort_key)

    print("=" * 60)
    print(f"✅ 待办清单 · 共 {len(all_tasks)} 件")
    print("=" * 60)

    for i, t in enumerate(all_tasks, 1):
        stars = "⭐" * t['priority']
        print(f"\n{i}. [{t['deadline']}] {t['task']}")
        print(f"   课程：{t['course']}  {stars}")


def show_course_detail(courses, course_id):
    """查看某一门课的详情"""
    course = None
    for c in courses:
        if c['id'] == course_id:
            course = c
            break

    if not course:
        print(f"找不到课程：{course_id}")
        print("可用的 id：", ", ".join(c['id'] for c in courses))
        return

    print("=" * 60)
    print(f"📖 {course['name']}")
    print("=" * 60)
    print(f"\n优先级：{'⭐' * course['priority']}")
    print(f"状态：{course['status']}")
    print(f"当前进度：{course['chapter']}")

    print(f"\n--- 任务列表 ---")
    for i, t in enumerate(course['tasks'], 1):
        mark = "✅" if t['done'] else "⬜"
        print(f"  {i}. {mark} {t['name']} （截止：{t['deadline']}）")

    print(f"\n--- 笔记 ---")
    for note in course['notes']:
        print(f"  • {note}")


def show_by_priority(courses):
    """按优先级排序展示"""
    show_all(courses)  # 目前 show_all 就是按优先级排的


if __name__ == '__main__':
    courses = load_data()

    if len(sys.argv) == 1:
        show_all(courses)
    elif sys.argv[1] == '--todo':
        show_todo(courses)
    elif sys.argv[1] == '--priority':
        show_by_priority(courses)
    elif sys.argv[1] == '--course' and len(sys.argv) > 2:
        show_course_detail(courses, sys.argv[2])
    else:
        print("用法：")
        print("  python study_map.py              全部课程概览")
        print("  python study_map.py --todo       所有待办（按时间排）")
        print("  python study_map.py --priority   按优先级排序")
        print("  python study_map.py --course <id> 某门课详情")
