/*
 * 数据结构 第2章作业
 * 姓名：__________    学号：__________
 * 截止时间：10月31日 23:59（按课程通知，通知未注明年份）
 * 提交邮箱：助教姜博文 1729773236@bupt.edu.cn
 * 命名格式：参照课程格式使用 学号_姓名_第2章作业.xxx。
 * 多个文件请先打包再发送。三道习题均已补齐算法及运行样例。
 * 来源：数据结构-CH2-HW.doc。
 */

/*
 * 学习过程与 AI 辅助说明（2026-10-28 至 2026-10-29）
 *
 * 这份文件记录我练习、卡住、重写和修正的过程。核心算法与配套程序的
 * 完成方式不同，下面按真实对话记录说明，不把所有代码都称为独立完成。
 * 文中的“原注释/原话”来自我在聊天中写下的内容；其余过程说明由
 * ChatGPT 根据对话整理，不是当时逐字写下的日记。
 *
 * 第1题：我在已练习过此题的基础上，再次选择“寻找起止位置、计算长度、
 * 搬移、更新表长”的路线，自己写出了标记变量和算法初稿。
 * AI 指出了 if 内声明变量的作用域、搬移起点应为 start、边界未找到时的
 * 处理，以及结束查找的判断应放到循环外、变量拼写等问题；我据此重写，
 * 最后自己提交了完整函数。这里保留那版逻辑，不改成另一种算法。
 *
 * 第2题：AI 先提供完整程序的结构示例，并逐步讲解头结点、tail、
 * 创建新结点和连接顺序，也展示过建表循环；因此并非从未见过示例的独立解题。
 * 我随后自己组装函数。第一次漏了 malloc，并写了多余的首次接入判断；
 * 经过解释修正。次日复写时又卡在新结点的创建，AI 提醒并给出创建片段后，
 * 我自己写出连接语句，并重新组装完整函数。
 * 我逐步理解：tail->next 改结点字段，tail = newNode 改指针变量的地址值；
 * Node* 声明不自动创建结点，malloc 才申请新空间并返回地址。
 *
 * 第3题：我先想到栈，也尝试过相邻交换，后来自己发现“距离中间位置
 * 相同的元素对调”，用奇偶长度的例子推导并验证 n-i-1。
 * 在 AI 关于交换和循环终点的提问、示例提示下，我写出临时变量交换，
 * 确定 i<n/2，并完成函数；AI 提醒补上 i、temp 的类型声明。
 *
 * AI 参与编辑的部分：题目转录、排版、整理说明、部分解释性注释、
 * 数据结构框架、destroyList、内存申请失败处理、输出函数、测试函数、main、
 * 编译和边界样例验证。核心函数以我的最终写法为基础整理。
 * 这18组测试由 AI 编写并执行，不代表我已亲自逐项运行或掌握全部配套代码。
 *
 * 想留下的感受（我的原话）：
 * “这个感觉是我今天最大的实感。做完这一题，对链表的认识又深化了。”
 * “我不是给谁交差，我是展现学习成果。”
 */
#include <stdlib.h>
#include <stdio.h>

/* ==================== 习题1 顺序表删除 ====================
 * 题目：顺序表 L 中元素递增有序，删除所有大于 k1 而小于 k2 的元素。
 * 前提：0 <= L.length <= 100，k1 < k2。
 * 设计思路：找到闭区间 [start, end]，计算删除长度 len，
 * 从 start 起将后续元素向前覆盖，最后更新逻辑长度。
 * startvalid、endvalid 为1表示尚未找到对应边界，为0表示已找到。
 * 无起点则不删除；无右边界则删除到表尾；len 为0表示区间内无元素。
 * 时间复杂度 O(n)，额外空间复杂度 O(1)。
 */
struct SqList {
    int data[100];
    int length;
};

// 我的原注释：“我试试自己来写啦，这题已经遇见三次了，这是第三次。
// 第一次搓完了，第二次从纸面推的，但是没搓。这次在这里搓。”
// 我的原注释：“我感觉这是这三题里面最难的。某种角度。”
// 修改过程中的原注释：“再试！-21：12 26/10/29”
// 保留我的标记变量和闭区间搬移思路；以下为反馈后自行修正的版本。
void intervalDelete(SqList& L, int k1, int k2)
{
    //寻找删除起点
    int startvalid = 1;
    int endvalid = 1;
    int start, end, len;
    for (int i = 0; i < L.length; i++) {
        if (L.data[i] > k1 && startvalid) {
            start = i;
            startvalid = 0; //找到过start，就不执行此句赋值了
        }
        if (L.data[i] >= k2 && endvalid) {
            end = i - 1;
            endvalid = 0; //同理
        }
        if (!startvalid && !endvalid) break; //都找到了就退出，不用一直循环下去了
    }
    // 必须查找结束后再判断，而不是在尚未查完整张表时返回。
    if (startvalid) return;
    if (endvalid) end = L.length - 1;

    //删除区间长度：
    len = end - start + 1;
    //替换
    // 保留 start 之前的前缀，只覆盖删除位置及其后部。
    for (int i = start; i < L.length - len; i++) {
        L.data[i] = L.data[i + len];
    }
    //修改逻辑长度
    L.length = L.length - len;
}

/* ==================== 习题2 正序创建链表 ====================
 * 正序创建链表。假设线性表的数据元素存储在一维数组 A[n] 中，
 * 则从数组的第一个分量起，依次生成结点，并逐个插入到一个初始为
 * “空”的链表中。
 *
 * 转录说明：原文此处的线性表符号为嵌入公式；正文要求如上。
 * 设计思路：带头结点，使用 tail 尾插，按数组顺序逐个创建并连接结点。
 * 结点结构：data 存数据，next 存后继结点地址。采用带头结点的单链表。
 * createList：接收只读数组及有效长度，返回链表入口。
 * destroyList：释放整条链表。前提：length >= 0；非空数组有足够元素。
 * 建表思路：创建头结点；tail 记录末尾；每轮创建、填写、接入新结点。
 * 时间复杂度 O(length)，结点存储 O(length)，额外工作指针空间 O(1)。
 * 算法实现：见 createList；申请失败时释放已创建的结点并返回 NULL。
 * 测试：普通序列、空表、单元素、重复值和负数；验证长度、顺序及尾部 NULL。
 */

typedef struct Node {
    int data;
    struct Node* next;
} Node;

// AI补写的配套收尾函数：逐个释放结点，包含头结点。
// 我学习后的理解：先mark住下一站，再free当前结点，最后换存下一站地址。
void destroyList(Node* head)
{
    Node* current = head;
    while (current != NULL) {
        Node* nextNode = current->next;
        free(current);
        current = nextNode;
    }
}

// 从数组正序建表，返回头结点地址；申请内存失败时返回 NULL。
Node* createList(const int A[], int length)
{
    //建立头结点
    // AI补注：malloc 创建结点空间；Node* 变量用来保存这块空间的地址。
    // 文件扩展名为 .cpp，所以显式转换 malloc 返回的指针类型。
    Node* head = (Node*)malloc(sizeof(Node));
    // AI补写：申请失败处理。
    if (head == NULL) {
        return NULL;
    }
    // 头结点的 data 不参与使用；空链表的头结点 next 为 NULL。
    head->next = NULL;

    //我的原注释：建立工作指针指向最后一个有效元素,初始的时候指向head指向的位置。
    //整理后补充：这里更准确地说是末尾结点；开始时头结点也暂时是末尾。
    Node* tail = head;

    //开始填入数据
    for (int i = 0; i < length; i++) {
        // 每轮申请一个独立结点，再填入本轮的数组元素。
        Node* newNode = (Node*)malloc(sizeof(Node));
        if (newNode == NULL) {
            // 失败处理是配套代码：释放已经创建的部分，避免内存泄漏。
            destroyList(head);
            return NULL;
        }
        newNode->data = A[i];
        newNode->next = NULL;

        // 改的是当前末尾结点内部的 next 字段，真正建立连接。
        // 第一轮 tail 与 head 地址相同，所以不必另写 head->next。
        tail->next = newNode;
        // 改的是 tail 变量保存的地址；结点本身没有移动。
        tail = newNode;
    }

    //我的原注释：返回头结点，此时链表已经建完
    return head;
}

/* ==================== 习题3 原地逆置 ====================
 * 题目：线性表存放在数组 A[arraySize] 的前 n 个位置，编写函数原地逆置。
 * 只允许使用常数个新增的辅助存储空间。
 * 输入约定：0 <= n <= 数组容量；n > 0 时 A 指向至少 n 个有效整数。
 * 结果：直接修改 A 的前 n 个元素，数组其余位置不变。
 *
 * 设计思路：下标 i 与 n-i-1 关于中间位置对称，用 temp 完成交换。
 * 只遍历前 n/2 个位置，避免一对元素被交换两次。
 * 整数除法中 5/2 为2，6/2 为3；奇数长度的中间元素无需移动。
 *
 * 函数说明：reverseArray 接收数组及有效长度，无返回值。
 * 时间复杂度：O(n)，共交换 floor(n/2) 次。
 * 额外空间复杂度：O(1)，仅使用 i、temp 等固定数量的变量。
 * 测试：main 覆盖奇数、偶数、单元素、空表、仅逆置有效前缀。
 */

// 我的推导原话：“其实相当于距离中间位置相同的元素对调，是不是？”
// 我用奇偶两组例子验证了 n-i-1，再写出下面的函数。
// AI提醒补齐变量类型；算法保留我的最终写法。
void reverseArray(int A[], int n)
{
    //遍历
    for (int i = 0; i < n / 2; i++) {
        //交换位置对称的元素
        // AI补注：先保存左侧的值，避免被右侧覆盖后丢失。
        int temp = A[i];
        A[i] = A[n - i - 1];
        A[n - i - 1] = temp;
    }
}

// 以下输出、样例检查与 main 均由AI补写，供我观察和验证核心算法。
// 测试所用数组不属于逆置算法使用的辅助空间。
void printArray(const int A[], int length)
{
    printf("[");
    //开始填入数据
    for (int i = 0; i < length; i++) {
        if (i > 0) printf(" ");
        printf("%d", A[i]);
    }
    printf("]");
}

// expected 是测试用的预期结果，不参与 reverseArray 的计算。
bool runReverseExample(const char* name, int A[], int n,
                       int arraySize, const int expected[])
{
    printf("%s\nBefore: ", name);
    printArray(A, arraySize);
    reverseArray(A, n);
    printf("\nAfter:  ");
    printArray(A, arraySize);

    bool passed = true;
    for (int i = 0; i < arraySize; i++) {
        if (A[i] != expected[i]) passed = false;
    }
    printf("\nResult: %s\n\n", passed ? "PASS" : "FAIL");
    return passed;
}

// 配套验证：按顺序访问有效结点，跳过不存数据的头结点。
bool runListExample(const char* name, const int A[], int length)
{
    Node* head = createList(A, length);
    // AI补写：申请失败处理。
    if (head == NULL) {
        printf("%s: allocation failed\n", name);
        return false;
    }

    printf("%s\nList: [", name);
    Node* current = head->next;
    bool passed = true;
    //开始填入数据
    for (int i = 0; i < length; i++) {
        if (current == NULL) {
            passed = false;
            break;
        }
        if (i > 0) printf(" ");
        printf("%d", current->data);
        if (current->data != A[i]) passed = false;
        current = current->next;
    }
    // 读取 length 个结点后应恰好到 NULL，不能多结点或形成环。
    if (current != NULL) passed = false;
    printf("]\nResult: %s\n\n", passed ? "PASS" : "FAIL");

    destroyList(head);
    head = NULL; // 已释放后不再保留可误用的地址。
    return passed;
}

// 配套测试：检查删除后的有效长度和保留元素顺序。
bool runDeleteExample(const char* name, SqList L, int k1, int k2,
                      const int expected[], int expectedLength)
{
    printf("%s\nBefore: ", name);
    printArray(L.data, L.length);
    intervalDelete(L, k1, k2);
    printf("\nAfter:  ");
    printArray(L.data, L.length);
    bool passed = (L.length == expectedLength);
    if (passed) {
        for (int i = 0; i < expectedLength; i++) {
            if (L.data[i] != expected[i]) passed = false;
        }
    }
    printf("\nResult: %s\n\n", passed ? "PASS" : "FAIL");
    return passed;
}

int main()
{
    printf("=== Exercise 1: interval deletion ===\n");
    const int middleExpected[] = {1, 2, 4, 5};
    const int gapExpected[] = {1, 2, 5, 6};
    const int originalExpected[] = {1, 2, 3, 4, 5};
    const int tailExpected[] = {1, 2};
    const int frontExpected[] = {3, 4, 5};
    bool deletePassed = true;
    if (!runDeleteExample("Middle; keep endpoints", {{1,2,3,4,5},5}, 2,4,middleExpected,4)) deletePassed = false;
    if (!runDeleteExample("Gap contains no elements", {{1,2,5,6},4}, 2,4,gapExpected,4)) deletePassed = false;
    if (!runDeleteExample("No start found", {{1,2,3,4,5},5}, 5,8,originalExpected,5)) deletePassed = false;
    if (!runDeleteExample("Delete through tail", {{1,2,3,4,5},5}, 2,8,tailExpected,2)) deletePassed = false;
    if (!runDeleteExample("Delete prefix", {{1,2,3,4,5},5}, 0,3,frontExpected,3)) deletePassed = false;
    if (!runDeleteExample("Delete everything", {{1,2,3,4,5},5}, 0,6,NULL,0)) deletePassed = false;
    if (!runDeleteExample("All above interval", {{1,2,3,4,5},5}, -3,0,originalExpected,5)) deletePassed = false;
    if (!runDeleteExample("Empty list", {{0},0}, 2,4,NULL,0)) deletePassed = false;
    if (!runDeleteExample("Single element deleted", {{3},1}, 2,4,NULL,0)) deletePassed = false;
    printf("All interval-delete examples: %s\n\n", deletePassed ? "PASS" : "FAIL");
    printf("=== Exercise 2: create linked list ===\n");
    const int listValues[] = {3, 7, 2};
    const int listSingle[] = {8};
    const int listMixed[] = {-2, 7, 7, 0};
    bool listPassed = true;
    if (!runListExample("Normal order", listValues, 3)) listPassed = false;
    if (!runListExample("Empty list", NULL, 0)) listPassed = false;
    if (!runListExample("Single element", listSingle, 1)) listPassed = false;
    if (!runListExample("Duplicates and negative values", listMixed, 4)) listPassed = false;
    printf("All linked-list examples: %s\n\n", listPassed ? "PASS" : "FAIL");
    printf("=== Exercise 3: reverse array ===\n");
    int odd[] = {2, 3, 5, 7, 9};
    const int oddExpected[] = {9, 7, 5, 3, 2};
    int even[] = {2, 3, 5, 7, 9, 11};
    const int evenExpected[] = {11, 9, 7, 5, 3, 2};
    int single[] = {8};
    const int singleExpected[] = {8};
    int prefix[] = {3, 7, 2, 99, 100};
    const int prefixExpected[] = {2, 7, 3, 99, 100};

    bool passed = true;
    if (!runReverseExample("Odd length", odd, 5, 5, oddExpected)) passed = false;
    if (!runReverseExample("Even length", even, 6, 6, evenExpected)) passed = false;
    if (!runReverseExample("Single element", single, 1, 1, singleExpected)) passed = false;
    if (!runReverseExample("Empty list", NULL, 0, 0, NULL)) passed = false;
    if (!runReverseExample("Only first n elements", prefix, 3, 5, prefixExpected)) passed = false;

    printf("All reverse-array examples: %s\n", passed ? "PASS" : "FAIL");
    return (passed && listPassed && deletePassed) ? 0 : 1;
}