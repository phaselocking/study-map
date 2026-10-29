"""Rebuild the archive's portable data and source copies; never changes inputs.

Run: python scripts/import_archive.py --source <course-directory> --report <report.md>
Editorial claims below are curated from the classroom survey and original transcripts.
An absent next transcript is not synthesized. A missing known source is recorded.
"""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
PDFS = {
    'slides-2-1': 'Chapter2-Section1(1).pdf', 'slides-2-2': 'Chapter2-Section2(1).pdf',
    'slides-2-3': 'Chapter2-Section3(1).pdf', 'slides-2-4': 'Chapter2-Section4(2).pdf',
    'slides-3-1': 'Chapter3-Silde1(1).pdf', 'slides-3-2': 'Chapter3-Slide2(1).pdf',
    'notes-2': 'Chapter-2(1).pdf', 'notes-3': 'Chapter3(1).pdf',
}
PAGE_COUNTS = {'slides-2-1':61,'slides-2-2':46,'slides-2-3':66,'slides-2-4':74,
               'slides-3-1':38,'slides-3-2':32,'notes-2':63,'notes-3':48}
CONCEPTS = [
 ('measure','概率测度',['测量','概率公理'],'用满足公理的集合函数描述事件的概率。'),
 ('continuity','概率连续性',['连续性','可列可加性'],'把单调事件列的极限与概率联系起来。'),
 ('conditional-probability','条件概率',['乘法公式'],'在一个已知事件发生的条件下研究另一事件。'),
 ('total-bayes','全概率与贝叶斯',['先验','后验','信息更新'],'分类求结果，以及已知结果后的条件更新。'),
 ('independence','独立性',['相互独立','两两独立'],'发生与否不改变另一事件的概率规律；需明确假设。'),
 ('binomial','二项分布',['伯努利','多项分布'],'独立重复试验中的成功次数及其推广。'),
 ('random-variable','随机变量',['逆像','映射'],'通过实值函数把事件研究引到实数空间。'),
 ('cdf','CDF',['分布函数','累积分布'],'用阈值事件的概率统一描述随机变量的分布。'),
 ('geometric','几何分布',['负二项','首次成功'],'独立伯努利试验中首次成功前的等待次数。'),
 ('poisson','泊松分布',['稀有事件','计数'],'课堂着重从单位时间计数及时间尺度理解。'),
 ('exponential','指数分布',['无记忆性','失效率','等待时间'],'连续等待时间模型；无记忆性与常数失效率相联系。'),
 ('normal','正态分布',['标准化','分位点','二维正态'],'从一维密度与标准化，延伸到变换及二维条件分布。'),
 ('transform','随机变量函数变换',['分布函数法','单调变换','sin X'],'把新变量的事件转回已知变量，再研究分布。'),
 ('joint','联合分布',['联合密度','联合分布律'],'保留多个变量共同取值及其联系的信息。'),
 ('marginal','边缘分布',['投影法','行列求和'],'从联合分布中不再区分其余变量，得到单个变量规律。'),
 ('conditional-distribution','条件分布',['条件概率密度','截线','固定变量'],'固定一个变量的条件后，研究另一个变量的分布。'),
]

# date, source stem, title, summary, concepts, relevant PDF IDs, outline(title,text,time)
LESSONS = [
 ('2026-09-17','9.17','概率作为测量：定义与公理','从课程认知与学习方法，进入概率的函数视角和不重复测量。',['measure'],[],[
  ('课程认知与已有基础','老师默认样本空间与基本集合运算已有基础，主张理解定义和框架。','00:51:34'),
  ('曹冲称象引入测量','用分箱称量解释整体测量、分开测量及不重复测的条件。','00:58:12'),
  ('概率公理与有限可加','从三条公理，讨论空集概率和由可列可加性得到有限情形。','01:02:56')]),
 ('2026-09-21','9.21','不交分解、连续性与几何概型','把一般并集变成不交并；从有限计算走到事件列的连续性。',['measure','continuity'],[],[
  ('一般并集转不交并','依次从后面的集合中排除前面已有的部分，再使用可加性。','00:01:17'),
  ('帽子配对与加法公式','借配对问题研究至少有一个人取回自己帽子的概率。','00:27:11'),
  ('概率连续性','补充单调事件列及概率极限，进一步讨论零概率事件。','00:35:18'),
  ('几何概型的例子','蒲丰投针与约会问题以均匀模型、面积之比展开。','01:11:00')]),
 ('2026-09-24','9.24','条件概率、独立性与推理方向','把条件概率继续看作测量工具，再连接乘法、独立与全概率。',['conditional-probability','independence','total-bayes'],[],[
  ('条件概率仍是概率','固定条件后验证概率公理，说明旧的概率性质仍可使用。','00:07:13'),
  ('乘法公式与摸球','在不放回摸球中按次序表达条件与事件。','00:19:27'),
  ('独立性的定义与边界','从不改变概率规律引入独立，后区分互斥、两两独立和相互独立。','00:39:46'),
  ('全概率与贝叶斯开头','开始区分由原因求结果及已知结果后反看原因；下次继续展开。','01:17:11')]),
 ('2026-09-28','9.28','贝叶斯更新与伯努利模型','重用摸球模型串起公式，再以二项、多项模型和连续性收尾第一章。',['independence','total-bayes','binomial','continuity'],[],[
  ('独立假设简化计算','补充射击、串并联系统的概率计算。','00:03:07'),
  ('先验、后验与信息更新','从结果反看原因，继续讨论摸球和螺栓生产的模型。','00:15:12'),
  ('伯努利、二项与多项','从两个结果推广到多结果独立重复试验。','00:35:22'),
  ('回到连续性，结束第一章','补充连续性习题，并预告下一次引入随机变量。','01:18:18')]),
 ('2026-10-08','10.8','随机变量与 CDF：从事件到实数','用映射和逆像解释随机变量的必要性；CDF 成为统一入口。',['random-variable','cdf','total-bayes','continuity'],['slides-2-1','notes-2'],[
  ('为什么引入随机变量','抽象试验结果不便直接使用高数工具，先把结果映为实数。','00:05:09'),
  ('定义、逆像和复合关系','从值域出发找回事件，再由概率测量。严格可测范围的表述仍有疑点。','00:17:46'),
  ('常数、CDF 与性质','验证常数也是随机变量；讨论CDF的性质与概率连续性的联系。','00:52:50'),
  ('混合分布例子','通过硬币决定取常数或均匀取值，说明离散、连续不是穷尽分类。','01:28:59')]),
 ('2026-10-12','10.12','离散分布：等待、成功次数与计数','从分布律走向几何、负二项与泊松，重视模型所表达的随机量。',['cdf','geometric','binomial','poisson','independence'],['slides-2-2','notes-2'],[
  ('分布律与CDF','讨论可数取值、非负与归一化，以及分布律和阶梯CDF的关系。','00:08:17'),
  ('几何等待与无记忆性','以首次成功所需次数解释几何分布和过去不影响未来。','00:22:24'),
  ('第r次成功','用最后一次必成功、前面已有r−1次成功推广到负二项模型。','01:03:08'),
  ('泊松与时间尺度','讲泊松分布、二项近似，再引出单位时间计数与间隔时间。','01:10:15')]),
 ('2026-10-15','10.15','连续密度、指数等待与失效率','用小区间理解密度，指数分布成为本次重点。',['cdf','exponential','geometric'],['slides-2-3','notes-2'],[
  ('从CDF积分表示定义连续型','讨论密度、单点概率为零及CDF与求导的关系。','00:01:56'),
  ('小区间帮助理解密度','把密度乘以很小的区间宽度，与该区间概率联系起来。','00:22:34'),
  ('指数与几何的对应','从离散等待次数转向连续等待时间和无记忆性。','00:43:03'),
  ('常数失效率','用已存活条件下的下一小段时间失效概率解释失效率。','01:17:08')]),
 ('2026-10-19','10.19','泊松—指数联系与正态标准化','计数与间隔在课堂被连接起来，随后进入正态、查表与分位点。',['poisson','exponential','normal','transform'],['slides-2-3','slides-2-4','notes-2'],[
  ('泊松计数与指数间隔','用一段时间无到达与等待超过该时间的事件对应建立联系；完整过程假设仍需核实。','00:07:27'),
  ('正态的形状与参数','引入密度、中心及松散程度；后进入标准化。','00:25:45'),
  ('标准化、查表与分位点','把一般正态问题转成标准正态，讨论对称性、三σ及上分位点。','00:51:13'),
  ('变量函数的引子','伽马只作概览，末尾开始研究Y=g(X)，尚未展开全部方法。','01:29:02')]),
 ('2026-10-22','10.22','变量变换：从 CDF 到多分支','反复在平方和指数变换中比较方法与适用范围。',['transform','cdf','normal'],['slides-2-4','notes-2'],[
  ('复合变量与离散变换','先确定新变量取值，多个原值映到同一值时合并概率。','00:12:24'),
  ('CDF方法与平方例子','把新变量事件转回X的事件；困难在区域和积分限。','00:28:13'),
  ('严格单调公式','找反函数及其导数，再用于对数正态和线性变换。','00:57:21'),
  ('分段单调与下次预告','平方分成两个分支，末尾口头试举sin X，下一次再提。','01:18:03')]),
 ('2026-10-26','10.26','变换收尾，进入二维联合分布','补完sin X与F(X)变换，之后从映射进入二维联合CDF及分布律。',['transform','cdf','joint','normal'],['slides-2-4','slides-3-1','notes-2','notes-3'],[
  ('取值区间内的单调性','同一个平方函数在不同X取值区间上，公式适用性不同。','00:01:33'),
  ('sin X的两个反分支','课件题设为密度2x/π²，而不是上次口头试举的均匀分布。','00:08:21'),
  ('CDF均匀化与模拟背景','讲F(X)变换，最后结束第二章；证明的反函数条件有待核实。','00:30:47'),
  ('二维联合CDF和分布律','定义二维映射、矩形概率，举硬币和正方形，再转联合分布律。','00:50:06')]),
]

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def parse_transcript(path):
    raw = path.read_text(encoding='utf-8-sig')
    matches = list(re.finditer(r'^\[(\d{2}:\d{2}:\d{2})\]\s*([^：\n]+)：', raw, re.M))
    blocks = []
    for i, m in enumerate(matches):
        text = raw[m.end():matches[i+1].start() if i+1 < len(matches) else len(raw)].strip()
        text = re.split(r'\n\s*第\d+(?:部分|章)', text)[0].strip()
        blocks.append({'id':f'p{i+1:03d}', 'timestamp':m.group(1), 'speaker':m.group(2), 'text':text,
                       'line':raw[:m.start()].count('\n')+1})
    return blocks

def build(source, report):
    missing=[]; lessons=[]; transcripts={}
    (ROOT/'sources/transcripts').mkdir(parents=True, exist_ok=True)
    (ROOT/'sources/courseware').mkdir(parents=True, exist_ok=True)
    for pdf in sorted(source.glob('*.pdf')):
        shutil.copyfile(pdf, ROOT/'sources/courseware'/pdf.name)
    # Adapt only this copy's links; the original analytical report remains untouched.
    report_path = ROOT/'sources/analysis/课程勘察报告.md'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if report.is_file():
        text = report.read_text(encoding='utf-8-sig')
        for f in source.iterdir():
            if f.suffix.lower() in ('.txt','.pdf'):
                group = 'transcripts' if f.suffix.lower()=='.txt' else 'courseware'
                text = text.replace(str(f).replace('\\','/'), '../'+group+'/'+quote(f.name, safe=''))
        report_path.write_text('> 网页引用副本：仅将本机资料链接适配为同项目内的源文件副本，原报告未改动。\n\n'+text, encoding='utf-8')
    else:
        missing.append('课程勘察报告不可访问：'+str(report))

    def make(date, stem, title, summary, concept_ids, pdf_ids, outline, detailed=False):
        filename=stem+'概率.txt'; original=source/filename
        blocks=parse_transcript(original) if original.is_file() else []
        transcripts[date]=blocks
        if original.is_file(): shutil.copyfile(original, ROOT/'sources/transcripts'/filename)
        else: missing.append(filename)
        sources=[]
        if blocks: sources.append({'id':'transcript','label':filename,'path':'sources/transcripts/'+filename,'originalPath':'概率论与数理统计/'+filename,'kind':'transcript'})
        for key in pdf_ids:
            file=PDFS[key]
            if (source/file).is_file(): sources.append({'id':key,'label':file,'path':'sources/courseware/'+file,'originalPath':'概率论与数理统计/'+file,'kind':'courseware','pageCount':PAGE_COUNTS[key]})
            else: missing.append(file)
        if report_path.is_file(): sources.append({'id':'survey','label':'Codex课程勘察报告（含10.29增补）','path':'sources/analysis/课程勘察报告.md','originalPath':str(report),'kind':'analysis'})
        item={'id':date,'date':date,'title':title,'summary':summary,'conceptIds':concept_ids,'coverage':'detailed' if detailed else 'survey',
              'recording':{'missingOpeningSeconds':300 if detailed else None,'missingOpeningApprox':detailed,'lastTimestamp':blocks[-1]['timestamp'] if blocks else None},
              'sections':{k:[] for k in ['outline','explanations','examples','examTips','personalNotes','connections']},'sources':sources,
              'transcriptPath':'data/transcripts/'+date+'.json' if blocks else None}
        for n,(heading,body,time) in enumerate(outline,1):
            item['sections']['outline'].append(card('outline-'+str(n),heading,body,time))
        save(ROOT/'data/transcripts'/f'{date}.json', {'lessonId':date,'blocks':blocks})
        return item

    def ref(time): return {'sourceId':'transcript','timestamp':time}
    def page(key,n): return {'sourceId':key,'page':n}
    def card(id,title,text,time=None,kind='transcript_summary',formula=None,extra=None,emphasis=False,caution=None):
        result={'id':id,'title':title,'text':text,'sourceType':kind,'sources':([ref(time)] if time else [])+(extra or [])}
        if formula: result['formula']=formula
        if emphasis: result['emphasis']=True
        if caution: result['caution']=caution
        return result

    for data in LESSONS: lessons.append(make(*data))
    # Extra evidence-based examples and explicit emphasis for the survey lessons.
    extras={
      '2026-09-17':('曹冲称象','称量大象时，石头分箱且不能重复称，作为可加性的直观类比。','00:58:12','解释定义的理解作业','老师要求用自己的方式讲出概率定义的理解过程。','01:35:21'),
      '2026-09-21':('蒲丰投针','从针的角度和到平行线的距离刻画相交条件，再使用几何概型。','01:11:00','概率步骤与计算步骤','老师要求保留概率公式，冗长计算另做；不是只写答案。','00:33:05'),
      '2026-09-24':('不放回摸球','先用特殊球数情形说明条件概率，再推广到分类求概率。','00:20:11','独立性的假设','老师把独立性作为简化概率问题的重要理想假设。','00:52:42'),
      '2026-09-28':('摸球与贝叶斯','已知第二次摸到白球，再问第一次摸到白球的概率，改变推理方向。','00:19:52','用一个模型串起几个公式','老师建议借同一个摸球模型搞清条件、全概率与贝叶斯的逻辑。','00:29:45'),
      '2026-10-08':('硬币混合分布','正面取常数1，反面在[0,1]均匀取值，再用全概率求CDF。','01:29:38','分布函数要定义完整','老师明确提醒分段CDF覆盖全实数，少一个值会扣分。','01:19:11'),
      '2026-10-12':('首次与第二次成功','已知第二次成功在第n次，思考首次成功位置为何等可能。','00:51:19','先想结果，再计算','老师要求先形成对概率结果的判断，再用计算相互核验。','00:57:53'),
      '2026-10-15':('归一化例题','借含未知常数的密度题讨论求常数、区间概率与完整CDF。','00:25:59','答题写出概率依据','老师强调概率公式和范围，微积分长计算不作为课堂要求的主体。','00:27:49'),
      '2026-10-19':('一般正态标准化','课件例题X服从N(2,9)，通过减2除3转为标准正态再查表。','01:04:28','正态形式与符号需记忆','老师说一般考试不会把正态密度形式作为已知条件直接给出。','00:26:32'),
      '2026-10-22':('均匀变量的平方','X在[-1,1]均匀取值时，平方将两侧原像并入同一个y，比较CDF与分支求法。','00:28:13','写清事件与步骤','老师强调概率步骤、取值范围与必要文字说明，计算可以简化。','00:34:52'),
      '2026-10-26':('sin X','与英2.4第55页题设相对应：密度2x/π²，0<x<π；分为两个单调区间。','00:08:21','别漏取值范围之外','老师提醒取值范围外的分段是容易遗漏、也容易得分的部分。','00:12:43'),
    }
    for lesson in lessons:
        e=extras[lesson['id']]
        lesson['sections']['examples'].append(card('example-1',e[0],e[1],e[2]))
        lesson['sections']['explanations'].append(card('emphasis-1',e[3],e[4],e[5],emphasis=True))
    # Exam notes appear only where the existing evidence explicitly supports them.
    for date,time,title,text in [
      ('2026-09-17','00:28:54','成绩构成尚未定案','老师转述平时、期末可能各50%；细项和是否最终执行在当时尚不明确。'),
      ('2026-09-21','00:34:18','卷面保留概率依据','把微积分长计算放在草稿，试卷保留概率思路和结果；这是老师的课堂要求。'),
      ('2026-10-08','01:19:11','CDF不要漏定义域','分段结果需覆盖所有实数；老师提到漏值会扣分。'),
      ('2026-10-15','00:33:37','过程分的课堂提示','老师用例题强调定义、公式与完整分段；并非已经核实的官方评分表。'),
      ('2026-10-19','00:26:32','正态密度形式','老师提示应记住符号和形式，一般考试不会直接提供。'),
      ('2026-10-22','00:36:38','强调步骤','老师以题目中的关键概率步骤说明得分，要求按规范写作业。'),
      ('2026-10-26','00:40:27','本部往年例题线索','老师称相关变换例题在本部往年期中常用；不能据此说当前班必考。')]:
        next(l for l in lessons if l['id']==date)['sections']['examTips'].append(card('exam-1',title,text,time,emphasis=True))

    new=make('2026-10-29','10.29','联合、边缘与条件：信息与范围','从联合所保留的信息出发，以投影和固定条件后的截线理解边缘与条件密度。',['joint','marginal','conditional-distribution','conditional-probability','normal'],['slides-3-2','notes-3'],[
      ('联合与边缘的信息关系','录音从承接中的话开始，随后进入边缘CDF；不能补造漏录的引入。','00:00:00'),
      ('离散边缘：行列求和','不再区分另一变量取何值，把相应联合概率相加。','00:03:29'),
      ('连续边缘：投影与积分限','先确定投影范围，再固定坐标沿另一方向找到非零区域的上下边界。','00:10:17'),
      ('条件分布：先给定再研究','从离散条件概率进入连续条件密度，突出分母条件及固定变量的意义。','00:35:19'),
      ('反向条件及课堂纠错','从一个边缘和一个条件重建联合，再反向求条件；老师纠正了画错的区域。','01:08:30'),
      ('二维正态的截面直观','用切平面和归一化展示条件分布仍为正态，只展示结果，没有完整证明。','01:24:50')],True)
    s=new['sections']
    s['explanations']=[
      card('information-quote','联合保留更多信息','因为你联合的信息多，边缘信息少。','00:08:49','teacher_quote',emphasis=True),
      card('marginal-cdf','让另一变量取遍可能值','求X的边缘CDF时，让联合CDF中的y趋于正无穷；两个边缘通常不能唯一重建联合。','00:00:37',formula=r'F_X(x)=\lim_{y\to+\infty}F_{X,Y}(x,y)',extra=[page('slides-3-2',3)]),
      card('discrete-marginal','离散边缘分布律','固定X的某个值，不再区分Y的取值；用互不相交的事件求和，得到表格边缘的行或列和。','00:03:29',formula=r'p_{i\cdot}=\sum_jp_{ij},\qquad p_{\cdot j}=\sum_ip_{ij}',extra=[page('slides-3-2',4)]),
      card('projection','投影确定范围，截线确定积分限','老师先把非零区域投影到所求变量的坐标轴；范围外密度为0。范围内固定该坐标，再沿另一个方向找积分上下限。','00:18:15',formula=r'f_X(x)=\int_{-\infty}^{+\infty}f_{X,Y}(x,y)\,dy',extra=[page('slides-3-2',7)],emphasis=True),
      card('conditional-density','条件密度及分母条件','在f_Y(y)>0的条件值处，用联合密度除以Y的边缘密度。老师主要讲方法，对证明只作简述。','00:44:40',formula=r'f_{X\mid Y}(x\mid y)=\frac{f_{X,Y}(x,y)}{f_Y(y)},\quad f_Y(y)>0',extra=[page('slides-3-2',16)]),
      card('fixed-condition','固定条件后的范围','给定Y=y后，研究X在该水平截线上的取值；不能把整片区域的变化与固定条件混在一起。范围外仍需写0。','00:55:34',extra=[page('slides-3-2',21)],emphasis=True),
      card('rebuild-joint','边缘与条件补回联系','仅有两个边缘通常不够；有一个边缘，再有该条件下另一变量的分布，便可按乘法关系构造联合。','00:47:02',formula=r'f_{X,Y}(x,y)=f_Y(y)f_{X\mid Y}(x\mid y)',extra=[page('slides-3-2',24)]),
      card('normal-section','二维正态：截面还需归一化','老师用草帽形密度曲面与平行于XOZ的切平面作直观介绍；截线本身的面积未必为1，需归一化，结果仍是正态。','01:24:50',extra=[page('slides-3-2',28),page('slides-3-2',31)]),
    ]
    s['examples']=[
      card('curved-marginals','曲边区域：同一密度求两个边缘','课件题设为f(x,y)=4x，0≤x≤1且0≤y≤x²。求X边缘时积分限为0到x²；求Y边缘时X从√y到1。公式和题设经课件核对，不能照抄破损转录。','00:23:28',formula=r'f_X(x)=4x^3\ (0<x<1),\qquad f_Y(y)=2(1-y)\ (0<y<1)',extra=[page('slides-3-2',10),page('slides-3-2',12)]),
      card('disk','单位圆上的投影例子','老师另外举单位圆均匀分布，以圆的上下边界寻找边缘积分限。转录一度把X范围记为0到1，前后又出现−1到1及正负平方根。','00:29:12',caution='缺原始板书；不按不一致的转录生成确定的逐步题解。'),
      card('curved-conditional','固定Y后的曲边条件密度','重用4x曲边题。固定0<y<1后，X的非零范围为√y到1；除以边缘2(1−y)，得到2x/(1−y)。','00:57:12',formula=r'f_{X\mid Y}(x\mid y)=\frac{2x}{1-y},\quad \sqrt y<x<1,\ 0<y<1',extra=[page('slides-3-2',21),page('slides-3-2',22)],caution='课件第22页把y=1包含在范围中，但此处分母为0；网页使用分母为正的内部条件范围。端点版本需另行规定。'),
      card('reverse-conditional','反向条件：先联合，再边缘，再除法','课件给Y边缘3y²及条件密度2x/y²（0<x<y<1），重建联合6x；求X边缘后再求Y给定X的条件。老师先画错方向，01:18:31承认图错，01:19:23改为从x到1积分。','01:08:30',formula=r'f_X(x)=\int_x^1 6x\,dy=6x(1-x),\qquad f_{Y\mid X}(y\mid x)=\frac{1}{1-x},\ x<y<1,\ 0<x<1',extra=[ref('01:18:31'),ref('01:19:23'),page('slides-3-2',23),page('slides-3-2',25),page('slides-3-2',26)],caution='纠正前的0到x积分及6x²不是最终答案。课件第26页公式在x=1也不能直接使用。'),
    ]
    s['examTips']=[
      card('exam-format','条件固定与卷面写法','老师反复强调先交代条件值与分母要求，再写剩余变量的函数及范围；把固定截线写成整片区域的变化，是他重点提示的失分问题。','00:51:25',extra=[ref('00:59:07'),ref('01:23:41')],emphasis=True,caution='关于给0分的说法记为老师的课堂要求，未核验官方评分细则。含x、y的记号也可能表示一族条件密度，不能扩写为这种记法一律错误。'),
      card('exam-tendency','条件密度题的命题倾向','老师讨论这类题常见，并说“如果我们期末考试，我们也会”。这是课堂命题倾向提示，不是正式考题或已经确定的考试范围。','00:45:53',emphasis=True),
      card('exam-endpoints','端点与分母也要检查','老师通过投影区间端点讨论条件密度定义的分母要求，提醒不要漏掉必须处理的点。','01:03:34',extra=[ref('01:05:47'),ref('01:07:06')],emphasis=True),
    ]
    new['sources'].append({'id':'personal','label':'本次聊天中的学习体验自述','path':None,'originalPath':None,'kind':'personal'})
    s['personalNotes']=[card('personal-1029','发现缺口后，主动追索框架','我迟到了，开头约5分钟没录到；这个缺口反而推动我努力补上一开始的框架，后面有认真听。','', 'personal_record',extra=[{'sourceId':'personal'}])]
    s['connections']=[
      card('connection-multiplication','第一章乘法思想回到联合密度','这是跨课整理分析：9.24的条件概率与乘法思路，在本次“边缘乘条件构造联合”中有可辨认的延续；不把两个边缘误当成已包含变量联系。','00:47:02','ai_analysis',extra=[{'sourceId':'survey'}]),
      card('connection-region','从逆像区域到投影、截线','对照10.22、10.26与本次课堂，可以看到老师把范围分析继续具体化为投影和固定条件后的截线。这是材料之间的分析连接。','00:33:49','ai_analysis',extra=[ref('00:55:34'),{'sourceId':'survey'}]),
      card('connection-next','下一次可能进入独立性','本次推进到英3.2末尾，英3.3从条件分布引入独立性；因此可能接独立性，也可能先补题。尚无下一次课堂记录。',None,'ai_analysis',extra=[{'sourceId':'survey'}]),
    ]
    new['recording']['note']='开头约5分钟未录到（用户自述）；原始时间戳从现存录音起点计时，不整体加5分钟。'
    lessons.append(new)

    # Conservative analytical links for earlier lessons; one per lesson, never a fabricated quote.
    links={
      '2026-09-17':('measure','先有不重复测量，后有不交分解','本次测量类比为9.21的集合分解提供可对照的背景。','00:58:12'),
      '2026-09-21':('continuity','连续性在CDF处再次使用','本次补充的概率连续性，在10.8讨论CDF极限和右连续时再次出现。','00:35:18'),
      '2026-09-24':('conditional-probability','同一个摸球模型的延续','10月29日边缘与条件构造联合，可与本次乘法和条件的思路对照。','00:19:27'),
      '2026-09-28':('binomial','从次数模型到随机变量','伯努利与多结果试验先提供模型，后续随机变量给出统一描述。','00:35:22'),
      '2026-10-08':('cdf','CDF作为后续统一入口','离散分布律、连续密度和函数变换，后面都能回到CDF与事件表达。','00:58:25'),
      '2026-10-12':('geometric','离散与连续的等待对象','几何等待次数与下一次指数等待时间具有课堂可对照的共同背景。','00:22:24'),
      '2026-10-15':('exponential','从等待时间走到计数联系','指数等待时间将在10.19与泊松计数发生明确联系。','00:43:03'),
      '2026-10-19':('normal','标准化也是变量变换','后续线性变换公式会把本次标准化放到更一般的形式中。','00:40:44'),
      '2026-10-22':('transform','分段单调方法尚有后续','10.26继续补完sin X，并强调在原变量实际取值区间上看单调性。','01:35:41'),
      '2026-10-26':('joint','新录音修正了先前预测','原勘察推测可能先补联合密度；现有10.29录音已进入边缘分布，漏录部分不能反推。','00:50:06'),
    }
    for l in lessons[:-1]:
        _,title,text,time=links[l['id']]
        l['sections']['connections'].append(card('connection-1',title,text,time,'ai_analysis',extra=[{'sourceId':'survey'}]))
    # Validate every editorial timestamp and every verbatim quote against its own transcript.
    for l in lessons:
        by_time={b['timestamp']:b for b in transcripts[l['id']]}
        ids={s['id'] for s in l['sources']}
        for section,cards in l['sections'].items():
            for c in cards:
                for r in c['sources']:
                    if r['sourceId'] not in ids: raise ValueError((l['id'],c['id'],'source',r))
                    if 'timestamp' in r:
                        if r['timestamp'] not in by_time: raise ValueError((l['id'],c['id'],'timestamp',r))
                        r['line']=by_time[r['timestamp']]['line']
                if c['sourceType']=='teacher_quote':
                    if not any(c['text'] in by_time[r['timestamp']]['text'] for r in c['sources'] if 'timestamp' in r):
                        raise ValueError('Nonverbatim quote: '+c['id'])
        l['recording']['segmentCount']=len(transcripts[l['id']])
        for src in l['sources']:
            if src['path']:
                p=ROOT/src['path']
                if not p.is_file(): raise ValueError('Missing portable source: '+str(p))
                src['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    concepts=[]
    for id,name,aliases,description in CONCEPTS:
        concepts.append({'id':id,'name':name,'aliases':aliases,'description':description,
          'lessonIds':[l['id'] for l in lessons if id in l['conceptIds']],'relations':[]})
    for origin,target,type_,date,time,text in [
      ('conditional-probability','total-bayes','classroom','2026-09-28','00:29:45','老师重用同一个摸球模型连接条件概率、全概率和贝叶斯。'),
      ('geometric','exponential','classroom','2026-10-15','00:43:03','课堂从几何等待次数引入指数等待时间与无记忆性。'),
      ('poisson','exponential','classroom','2026-10-19','00:12:52','课堂把无到达的计数事件与等待超过t的事件对应；完整过程假设仍需核实。'),
      ('joint','marginal','classroom','2026-10-29','00:08:49','课堂明确区分联合的信息与两个边缘的信息。'),
      ('marginal','conditional-distribution','classroom','2026-10-29','00:47:02','老师用边缘乘条件解释联合分布的构造。'),
      ('normal','conditional-distribution','classroom','2026-10-29','01:24:50','二维正态的条件分布仅作几何直观及结果展示。'),
      ('transform','marginal','analysis','2026-10-29','00:33:49','整理分析：从前两课的范围分析，到本次投影与截线，是可对照的方法延续。')]:
        next(c for c in concepts if c['id']==origin)['relations'].append({'targetId':target,'type':type_,'text':text,'sources':[{'lessonId':date,'sourceId':'transcript','timestamp':time}]})
    payload={'schemaVersion':1,'course':{'title':'概率论与数理统计','semester':'2026 秋季学期','progress':{'label':'第三章 · 边缘分布与条件分布','asOf':'2026-10-29'},'archiveTitle':'Probability Archive｜概率论课堂档案馆'},
      'sourceTypes':{'teacher_quote':'老师原话（转录）','transcript_summary':'课堂转录摘要','ai_analysis':'AI 整理分析','personal_record':'我的学习记录'},
      'evidencePolicy':'时间戳为转录段首；课件页码为PDF物理页。老师评分说法不等于已核实的官方规则。无原始录音链接，不生成音频跳转。',
      'missingMaterials':['第一章PDF及老师自编连续性习题','原始音视频、板书和确切投影版本','正式考试安排与评分细则','10.29开头约5分钟录音']+sorted(set(missing)),
      'lessons':lessons}
    save(ROOT/'data/lessons.json',payload)
    save(ROOT/'data/concepts.json',{'schemaVersion':1,'concepts':concepts})
    save(ROOT/'data/import-manifest.json',{'schemaVersion':1,'sourceDirectory':str(source),'analysisReport':str(report),'lessonCount':len(lessons),'segmentCount':sum(len(b) for b in transcripts.values()),'missing':sorted(set(missing)),'originalInputsModified':False})
    print(json.dumps({'lessons':len(lessons),'segments':sum(len(b) for b in transcripts.values()),'concepts':len(concepts),'missing':sorted(set(missing))},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--force',action='store_true',help='Replace only generated files in this probability-atlas project; manual JSON edits will be replaced.')
    args=parser.parse_args()
    if not args.source.is_dir(): parser.error('Source directory is not accessible')
    if not args.force and any((ROOT/'data'/name).exists() for name in ['lessons.json','concepts.json']):
        parser.error('Archive JSON already exists. Keep manual edits and add new lessons directly, or explicitly use --force to regenerate this project only.')
    build(args.source.resolve(),args.report.resolve())
