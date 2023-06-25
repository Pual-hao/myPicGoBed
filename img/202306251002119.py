# coding= gbk
import re
import string
import tkinter as tk
from tkinter import scrolledtext


class Solution:
    @staticmethod
    def loadfile(filename: str):
        di = dict()
        with open(filename, 'r', encoding='utf-8') as fl:
            li = []
            firstline = True
            for line in fl:
                if firstline:
                    # b = re.findall('[A-Z].+', line).pop()[0]
                    u = re.findall('[A-Z].+', line).pop();
                    b = u[0]
                    firstline = False
                li.append(re.findall('[A-Z].+', line).pop())
            for item in li:  # 合并文法中所有相同的非终结符
                if item[0] not in di.keys():
                    di[item[0]] = []
                    di[item[0]].append(item[3:])
                else:
                    di[item[0]].append(item[3:])
            for key in di.keys():
                for item in di[key]:
                    if '|' in item:
                        di[key].extend(item.split('|'))
                        di[key].remove(item)
        return di, b

    @staticmethod
    def eliminate_left_recursion(di):
        new_di = {}

        non_terminals = di.keys()
        for A in non_terminals:
            productions = di[A]
            new_productions = []
            new_nonterminal = A + "'"
            # 如E->E+T|T
            # 处理左递归产生式 产生+TE'
            for alpha in productions:
                if alpha[0] == A:
                    new_productions.append(alpha[1:] + new_nonterminal)

            # 如果有左递归式存在
            if new_productions:
                # 添加新的非终结符
                new_di[new_nonterminal] = ["ε"]
                # 处理E,将E->E+T|T 转成E->TE'
                for alpha in productions:
                    if alpha[0] != A:
                        new_di[A] = [alpha + new_nonterminal]
                # 处理E' 将E'->+TE'加入E'中
                for alpha in new_productions:
                    new_di[new_nonterminal].append(alpha)

            else:
                new_di[A] = productions

        return new_di

    @staticmethod
    def getfistset(gramset: dict) -> dict:  # 求文法的first集
        def getfirst(N: str):  # 求该非终结符的first集
            for item in gramset[N]:
                # 当最左字符为终结符时,直接加入first集
                if item[0] not in string.ascii_uppercase and item[0] not in res[N]:
                    res[N].append(item[0])
                else:  # 最左字符为非终结符
                    if bd[item[0]] is False:  # 该非终结符first未求出时,先求出该非终结符的first集
                        getfirst(item[0])
                    res[N].extend(filter(lambda x: x != 'ε', res[item[0]]))
                    n = 0
                    # 如果该非终结符的first集中存在ε
                    while n + 1 < len(item) and 'ε' in res[item[n]]:
                        # 下一位为终结符时,将该终结符加入first集中
                        if item[n + 1] in string.ascii_lowercase:
                            res[N].append(item[n + 1])
                            break
                        # 下一位为非终结符时,将该非终结符的first集也加入N的first集中
                        # 注意需要判断该非终结符是否含符号'
                        else:
                            # 若该非终结符含符号'
                            if n + 2 < len(item) and item[n + 2] == "'":
                                # python切片左闭右开,所以右边界是n+3
                                if bd[item[n + 1:n + 3]] is False:
                                    getfirst(item[n + 1:n + 3])
                                res[N].extend(filter(lambda x: x != 'ε', res[item[n + 1:n + 3]]))
                            else:
                                if bd[item[n + 1]] is False:
                                    getfirst(item[n + 1])
                                res[N].extend(filter(lambda x: x != 'ε', res[item[n + 1]]))
                            n += 1  # 送入下一次循环, 需要用来判断该终结符中是否也含ε
                    # 如果n的值能够到达最后一个字符,代表前面的字符都包含有ε
                    if n is len(item) - 1 and 'ε' in res[item[n]]:
                        res[N].append('ε')
            bd[N] = True

        res = dict()  # 存放非终结符的first集的字典,键为非终结符,值为该非终结符的first集的集合
        bd = dict()
        for key in gramset.keys():
            res[key] = []
            bd[key] = False
        for key in gramset.keys():
            if bd[key] is False:
                getfirst(key)
        for key in gramset.keys():  # 将字典中的值类型从列表转成集合,去除掉相同的元素
            res[key] = list(set(res[key]))
        # print(f'firstset:{res}')
        return res

    @staticmethod
    def getfollowset(gramset: dict, fiset: dict, b: str) -> dict:
        def getfollow(N: str):  # 求该非终结符的follow集
            for key in gramset.keys():
                for item in gramset[key]:
                    for i in range(len(item)):
                        # 该非终结符不含'时
                        if len(N) == 1:
                            if item[i] is N:
                                if i + 1 is len(item):  # N在右式的最右边
                                    if bd[key] is False and key != N:
                                        getfollow(key)
                                    res[N].extend(res[key])
                                else:  # 不在右式的最右边时候
                                    # 为非终结符时,则加上其first集
                                    if item[i + 1] in string.ascii_uppercase:
                                        # 该非终结符含'时
                                        if i + 2 < len(item) and item[i + 2] == "'":
                                            res[N].extend(filter(lambda x: x != 'ε', fiset[item[i + 1:i + 3]]))
                                            if "ε" in fiset[item[i + 1:i + 3]] and i + 2 == len(item) - 1:
                                                if bd[key] is False:
                                                    getfollow(key)
                                                res[N].extend(res[key])
                                        # 不含'时
                                        else:
                                            res[N].extend(filter(lambda x: x != 'ε', fiset[item[i + 1]]))
                                            if 'ε' in fiset[item[i + 1]] and i + 1 == len(item) - 1:
                                                if bd[key] is False:
                                                    getfollow(key)
                                                res[N].extend(res[key])

                                    else:
                                        # 为非终结符时,需要排除符号'
                                        if item[i + 1] != "'":
                                            res[N].append(item[i + 1])
                        # 该非终结符含'时
                        else:
                            if i + 1 < len(item):
                                if item[i:i + 2] == N:
                                    if i + 1 is len(item) - 1:  # N在右式的最右边
                                        if bd[key] is False and key != N:
                                            getfollow(key)
                                        res[N].extend(res[key])
                                    else:  # 不在最右边
                                        # 下一个为非终结符
                                        if item[i + 2] in string.ascii_uppercase:
                                            # 该非终结符含符号'
                                            if i + 3 < len(item) and item[i + 3] == "'":
                                                res[N].extend(filter(lambda x: x != 'ε', fiset[item[i + 2:i + 4]]))
                                                # 该终结符处于最右边时
                                                if 'ε' in fiset[item[i + 2:i + 4]] and i + 3 == len(item) - 1:
                                                    if bd[key] is False:
                                                        getfollow(key)
                                                    res[N].extend(res[key])
                                            # 该非终结符不含'
                                            else:
                                                res[N].extend(filter(lambda x: x != 'ε', fiset[item[i + 2]]))
                                                # 该终结符处于最右边时
                                                if 'ε' in fiset[item[i + 2]] and i + 2 == len(item) - 1:
                                                    if bd[key] is False:
                                                        getfollow(key)
                                                    res[N].extend(res[key])
                                        # 下一个为终结符
                                        else:
                                            res[N].append(item[i + 2])
            bd[N] = True

        res = dict()  # 存放非终结符的FOLLOW集的字典,键为非终结符,值为该非终结符的follow集的集合
        bd = dict()
        for key in gramset.keys():
            res[key] = []
            bd[key] = False
        res[b].append('#')
        for key in gramset.keys():
            if bd[key] is False:
                getfollow(key)
        for key in gramset.keys():  # 将字典中的值类型从列表转成集合,去除掉相同的元素
            res[key] = list(set(res[key]))
            # if "'" in res[key]:
            #     res[key].remove("'")
        # print(f'followset:{res}')
        return res

    @staticmethod
    def prelist(gramset: dict, fiset: dict, follset: dict):  # 创建预测表
        nter = []  # 非终结符列表
        ter = []  # 终结符(与#)列表
        for key in gramset.keys():
            nter.append(key)
        for key in fiset.keys():
            ter.extend(filter(lambda x: x != 'ε', fiset[key]))
        for key in follset.keys():
            ter.extend(follset[key])
            ter = list(set(ter))  # 去掉终结符列表相同项
        ntdic = dict()
        tedic = dict()
        for i in range(len(nter)):
            ntdic[nter[i]] = i
        for i in range(len(ter)):
            tedic[ter[i]] = i
        res = []
        for i in ntdic.keys():  # 非终结符
            temp = []
            for j in tedic.keys():  # 终结符
                for n in range(len(gramset[i])):
                    # 终结符在i的右式的第一个字符的first集中
                    if gramset[i][n][0] in string.ascii_uppercase and j in fiset[gramset[i][n][0]]:
                        temp.append(gramset[i][n])
                        break
                    # 终结符是i的右式的第一个字符时
                    elif gramset[i][n][0] not in string.ascii_uppercase and j is gramset[i][n][0]:
                        temp.append(gramset[i][n])
                        break
                    # 终结符在取ε时候满足处于i的follow集中
                    elif gramset[i][n][0] == 'ε' and j in follset[i]:
                        temp.append('ε')
                        break
                    # 直到最后一个产生式也不满足上述三种条件时，设置为Error
                    if n == len(gramset[i]) - 1:
                        temp.append('Error')
            res.append(temp)
        # 下面代码为打印分析表的格式
        print(tedic)
        print(ntdic)
        print('预测分析表如下:')
        for key in tedic.keys():
            print(key, end='    ')
        print()
        for i in ntdic.keys():
            print(f'{i}:', end='')
            for j in tedic.keys():
                print(f'{res[ntdic[i]][tedic[j]]}', end='    ')
            print()
        return res, ntdic, tedic


class FirstWindows:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry(f"400x300+{self.root.winfo_screenwidth() // 2 - 200}"
                           f"+{self.root.winfo_screenheight() // 2 - 150}")
        self.root.title("LL(1)文法分析器")

        label1 = tk.Label(self.root, text="请输入文法的文件地址")
        label1.pack()

        frame1 = tk.Frame(self.root)
        frame1.pack()

        label2 = tk.Label(frame1, text="请输入要分析的文法")
        label2.pack(side=tk.LEFT)

        self.text_box = tk.Entry(frame1)
        self.text_box.pack(side=tk.LEFT)

        button = tk.Button(self.root, text="分析文法", command=self.analyze_grammar)
        button.pack()

        self.root.mainloop()

    def analyze_grammar(self):
        # 在这里实现按钮点击后的操作
        SecondWindows(self.text_box.get())


class SecondWindows:
    def __init__(self, filename: str):
        root = tk.Tk()
        root.geometry(f"1000x600+{root.winfo_screenwidth() // 2 - 500}"
                      f"+{root.winfo_screenheight() // 2 - 300}")
        root.title('LL(1)分析')
        # 第一个框架用来放文法,first集,follow集和预测表
        frame1 = tk.Frame(root)
        frame3 = tk.Frame(frame1)
        frame3.pack()
        frame4 = tk.Frame(frame1)
        frame4.pack()
        frame5 = tk.Frame(frame1)
        frame5.pack()

        frame1.grid(row=0, column=0)

        # 文法板块
        lbwenfa = tk.Label(frame3, text='文法:')
        lbwenfa.pack()
        lbtext_areawenfa = scrolledtext.ScrolledText(frame3, wrap=tk.WORD, width=60, height=10)
        lbtext_areawenfa.pack()
        self.gramli, self.begin = Solution.loadfile(filename)
        for key in self.gramli.keys():
            st = '|'.join(self.gramli[key])
            lbtext_areawenfa.insert(tk.END, f'{key}->{st}\n')
        lbtext_areawenfa.config(state="disabled")

        lbwenfa1 = tk.Label(frame3,text="消除左递归:")
        lbwenfa1.pack()
        lbtext_areawenfa1 = scrolledtext.ScrolledText(frame3, wrap=tk.WORD, width=60, height=10)
        lbtext_areawenfa1.pack()
        self.gramli = Solution.eliminate_left_recursion(self.gramli)
        for key in self.gramli.keys():
            st = '|'.join(self.gramli[key])
            lbtext_areawenfa1.insert(tk.END, f'{key}->{st}\n')
        lbtext_areawenfa1.config(state="disabled")


        # First和Follow集板块
        frame6 = tk.Frame(frame4)
        frame7 = tk.Frame(frame4)
        frame6.grid(row=0, column=0)
        frame7.grid(row=0, column=1)
        lbfirst = tk.Label(frame6, text='First集')
        lbfirst.pack()
        lbtext_areafirst = scrolledtext.ScrolledText(frame6, wrap=tk.WORD, width=30, height=10)
        lbtext_areafirst.pack()
        self.fistset = Solution.getfistset(self.gramli)
        for key in self.fistset.keys():
            st = ','.join(self.fistset[key])
            lbtext_areafirst.insert(tk.END, f'FIRST({key}) = {st}\n')
        lbtext_areafirst.config(state="disabled")
        lbfollow = tk.Label(frame7, text='Follow集')
        lbfollow.pack()
        lbtext_areafollow = scrolledtext.ScrolledText(frame7, wrap=tk.WORD, width=30, height=10)
        lbtext_areafollow.pack()
        self.followset = Solution.getfollowset(self.gramli, self.fistset, self.begin)
        for key in self.followset.keys():
            st = ','.join(self.followset[key])
            lbtext_areafollow.insert(tk.END, f'Follow({key}) = {st}\n')
        lbtext_areafollow.config(state="disabled")

        # 预测表板块
        lbpreli = tk.Label(frame5, text='预测表')
        lbpreli.pack()
        lbtext_areaprelist = scrolledtext.ScrolledText(frame5, wrap=tk.WORD, width=60, height=20)
        lbtext_areaprelist.pack()
        self.preli, self.ntdic, self.tdic = Solution.prelist(self.gramli, self.fistset, self.followset)
        for key in self.tdic.keys():
            lbtext_areaprelist.insert(tk.END, f'    {key}')
        lbtext_areaprelist.insert(tk.END, '\n')
        for i in self.ntdic.keys():
            lbtext_areaprelist.insert(tk.END, f'{i}:')
            for j in self.tdic.keys():
                lbtext_areaprelist.insert(tk.END, f'{self.preli[self.ntdic[i]][self.tdic[j]]}    ')
            lbtext_areaprelist.insert(tk.END, '\n')
        lbtext_areaprelist.config(state="disabled")

        # 第二个框架用来放输入串和过程
        frame2 = tk.Frame(root)
        frame2.grid(row=0, column=1, sticky="nsew")
        # 输入串
        frame8 = tk.Frame(frame2)
        frame8.pack()
        lbshuru = tk.Label(frame8, text='输入字符串:')
        lbshuru.pack(side=tk.LEFT)
        self.lbtext_box = tk.Entry(frame8)
        self.lbtext_box.pack(side=tk.LEFT)
        buton = tk.Button(frame2, text='确认', command=self.startdipose)
        buton.pack()
        # 过程
        lbpro = tk.Label(frame2, text='过程')
        lbpro.pack()
        self.progress = scrolledtext.ScrolledText(frame2, wrap=tk.WORD, width=60)
        self.progress.pack()
        self.progress.insert(tk.END, f'步骤    符号栈    输入串    所用表达式    \n')

        root.mainloop()

    def startdipose(self):
        self.dipose(self.lbtext_box.get() + '#', self.preli, self.ntdic, self.tdic, self.begin)

    def dipose(self, insrt: str, lis: list, ntdic: dict, tdic: dict, b: str):
        stack = ['#', b]
        step = 0
        self.progress.insert(tk.END, f'{step}    {stack}    {insrt}    \n')
        step += 1
        while len(stack) != 0:
            top = stack.pop()
            if top in ntdic.keys():  # 栈顶符号是非终结符
                if lis[ntdic[top]][tdic[insrt[0]]] != 'Error' and lis[ntdic[top]][tdic[insrt[0]]] != 'ε':
                    li = lis[ntdic[top]][tdic[insrt[0]]][::-1]
                    i = 0
                    while (i < len(li)):
                        if li[i] == "'" and i + 1 < len(li):
                            # 'E转成E'入栈
                            stack.append(li[i:i + 2][::-1])
                            i += 2
                        else:
                            stack.append(li[i])
                            i += 1
                    self.progress.insert(tk.END, f'{step}    {stack}    {insrt}    '
                                                 f'{top}->{lis[ntdic[top]][tdic[insrt[0]]]}\n')
                    step += 1
                    continue
                elif lis[ntdic[top]][tdic[insrt[0]]] == 'ε':  # 如果预测是ε,不需要入栈操作
                    self.progress.insert(tk.END, f'{step}    {stack}    {insrt}    '
                                                 f'{top}->ε\n')
                    step += 1
                    continue
                else:
                    self.progress.insert(tk.END, f'{step}    {stack}    {insrt}    '
                                                 f'Error')
                    break
            else:  # 栈顶符号是终结符
                if top == insrt[0]:  # 栈顶符号与第一个字符匹配
                    if top == '#':  # 匹配完所有字符
                        break
                    else:
                        insrt = insrt[1:]
                        self.progress.insert(tk.END, f'{step}    {stack}    {insrt}    \n')
                        step += 1
                        continue
                else:  # 栈顶符号不匹配
                    self.progress.insert(tk.END, f'{step}    {stack}    {insrt}    '
                                                 f'Error\n')
                    break


win = FirstWindows()

