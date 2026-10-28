/*
 * 数据结构 第2章作业
 * 姓名：__________    学号：__________
 * 截止时间：10月31日 23:59（按课程通知，通知未注明年份）
 * 提交邮箱：助教姜博文 1729773236@bupt.edu.cn
 * 命名格式：参照课程格式使用 学号_姓名_第2章作业.xxx。
 * 多个文件请先打包再发送。习题2已录入建表函数，其余题目待完成。
 * 来源：数据结构-CH2-HW.doc。
 */

#include <stdlib.h>

/* ==================== 习题1 顺序表删除 ====================
 * 设顺序表 L 中的数据元素递增有序，试编写算法删除表中所有大于 k1
 * 而小于 k2 的元素（k1 < k2）。
 *
 * 设计思路：TODO
 * 数据结构及函数说明：TODO
 * 算法实现：TODO
 * 测试与运行记录：TODO
 */

// TODO：在这里定义本题的数据结构与函数。

/* ==================== 习题2 正序创建链表 ====================
 * 正序创建链表。假设线性表的数据元素存储在一维数组 A[n] 中，
 * 则从数组的第一个分量起，依次生成结点，并逐个插入到一个初始为
 * “空”的链表中。
 *
 * 转录说明：原文此处的线性表符号为嵌入公式；正文要求如上。
 * 设计思路：TODO
 * 结点结构：data 存数据，next 存后继结点地址。采用带头结点的单链表。
 * createList：接收只读数组及有效长度，返回链表入口。
 * destroyList：释放整条链表。前提：length >= 0；非空数组有足够元素。
 * 建表思路：创建头结点；tail 记录末尾；每轮创建、填写、接入新结点。
 * 时间复杂度 O(length)，结点存储 O(length)，额外工作指针空间 O(1)。
 * 算法实现：TODO
 * 测试与运行记录：TODO
 */

typedef struct Node {
    int data;
    struct Node* next;
} Node;

// 配套收尾函数：逐个释放结点，包含头结点。
void destroyList(Node* head)
{
    while (head != NULL) {
        Node* nextNode = head->next;
        free(head);
        head = nextNode;
    }
}

// 从数组正序建表，返回头结点地址；申请内存失败时返回 NULL。
Node* createList(const int A[], int length)
{
    // malloc 创建结点空间；Node* 变量用来保存这块空间的地址。
    // 文件扩展名为 .cpp，所以显式转换 malloc 返回的指针类型。
    Node* head = (Node*)malloc(sizeof(Node));
    if (head == NULL) {
        return NULL;
    }
    // 头结点的 data 不参与使用；空链表的头结点 next 为 NULL。
    head->next = NULL;

    // 初始只有头结点，因此 tail 和 head 保存同一个地址。
    Node* tail = head;

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

    return head;
}

/* ==================== 习题3 原地逆置 ====================
 * 设有一个线性表，存放在一个一维数组 A[arraySize] 中的前 n 个
 * 数组元素位置。请编写一个函数将这个线性表原地逆置。
 * 原地逆置表示只能用常数个新增的辅助存储空间。
 *
 * 转录说明：原文的元素序列为嵌入公式，文本提取不完整；这里用
 * 等价的下标表示目标：A[0],...,A[n-1] 变为 A[n-1],...,A[0]。
 * 如需核对原始公式，请查看同目录“原始题目”中的附件。
 *
 * 设计思路：TODO
 * 函数说明：TODO
 * 算法实现：TODO
 * 时间与空间复杂度：TODO
 * 测试与运行记录：TODO
 */

// TODO：在这里编写逆置函数。

int main()
{
    // 尚未添加测试：习题2的核心函数已录入，本次不运行程序。
    return 0;
}
