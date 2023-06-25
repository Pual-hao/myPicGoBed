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
            for item in li:  # �ϲ��ķ���������ͬ�ķ��ս��
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
            # ��E->E+T|T
            # ������ݹ����ʽ ����+TE'
            for alpha in productions:
                if alpha[0] == A:
                    new_productions.append(alpha[1:] + new_nonterminal)

            # �������ݹ�ʽ����
            if new_productions:
                # ����µķ��ս��
                new_di[new_nonterminal] = ["��"]
                # ����E,��E->E+T|T ת��E->TE'
                for alpha in productions:
                    if alpha[0] != A:
                        new_di[A] = [alpha + new_nonterminal]
                # ����E' ��E'->+TE'����E'��
                for alpha in new_productions:
                    new_di[new_nonterminal].append(alpha)

            else:
                new_di[A] = productions

        return new_di

    @staticmethod
    def getfistset(gramset: dict) -> dict:  # ���ķ���first��
        def getfirst(N: str):  # ��÷��ս����first��
            for item in gramset[N]:
                # �������ַ�Ϊ�ս��ʱ,ֱ�Ӽ���first��
                if item[0] not in string.ascii_uppercase and item[0] not in res[N]:
                    res[N].append(item[0])
                else:  # �����ַ�Ϊ���ս��
                    if bd[item[0]] is False:  # �÷��ս��firstδ���ʱ,������÷��ս����first��
                        getfirst(item[0])
                    res[N].extend(filter(lambda x: x != '��', res[item[0]]))
                    n = 0
                    # ����÷��ս����first���д��ڦ�
                    while n + 1 < len(item) and '��' in res[item[n]]:
                        # ��һλΪ�ս��ʱ,�����ս������first����
                        if item[n + 1] in string.ascii_lowercase:
                            res[N].append(item[n + 1])
                            break
                        # ��һλΪ���ս��ʱ,���÷��ս����first��Ҳ����N��first����
                        # ע����Ҫ�жϸ÷��ս���Ƿ񺬷���'
                        else:
                            # ���÷��ս��������'
                            if n + 2 < len(item) and item[n + 2] == "'":
                                # python��Ƭ����ҿ�,�����ұ߽���n+3
                                if bd[item[n + 1:n + 3]] is False:
                                    getfirst(item[n + 1:n + 3])
                                res[N].extend(filter(lambda x: x != '��', res[item[n + 1:n + 3]]))
                            else:
                                if bd[item[n + 1]] is False:
                                    getfirst(item[n + 1])
                                res[N].extend(filter(lambda x: x != '��', res[item[n + 1]]))
                            n += 1  # ������һ��ѭ��, ��Ҫ�����жϸ��ս�����Ƿ�Ҳ����
                    # ���n��ֵ�ܹ��������һ���ַ�,����ǰ����ַ��������Ц�
                    if n is len(item) - 1 and '��' in res[item[n]]:
                        res[N].append('��')
            bd[N] = True

        res = dict()  # ��ŷ��ս����first�����ֵ�,��Ϊ���ս��,ֵΪ�÷��ս����first���ļ���
        bd = dict()
        for key in gramset.keys():
            res[key] = []
            bd[key] = False
        for key in gramset.keys():
            if bd[key] is False:
                getfirst(key)
        for key in gramset.keys():  # ���ֵ��е�ֵ���ʹ��б�ת�ɼ���,ȥ������ͬ��Ԫ��
            res[key] = list(set(res[key]))
        # print(f'firstset:{res}')
        return res

    @staticmethod
    def getfollowset(gramset: dict, fiset: dict, b: str) -> dict:
        def getfollow(N: str):  # ��÷��ս����follow��
            for key in gramset.keys():
                for item in gramset[key]:
                    for i in range(len(item)):
                        # �÷��ս������'ʱ
                        if len(N) == 1:
                            if item[i] is N:
                                if i + 1 is len(item):  # N����ʽ�����ұ�
                                    if bd[key] is False and key != N:
                                        getfollow(key)
                                    res[N].extend(res[key])
                                else:  # ������ʽ�����ұ�ʱ��
                                    # Ϊ���ս��ʱ,�������first��
                                    if item[i + 1] in string.ascii_uppercase:
                                        # �÷��ս����'ʱ
                                        if i + 2 < len(item) and item[i + 2] == "'":
                                            res[N].extend(filter(lambda x: x != '��', fiset[item[i + 1:i + 3]]))
                                            if "��" in fiset[item[i + 1:i + 3]] and i + 2 == len(item) - 1:
                                                if bd[key] is False:
                                                    getfollow(key)
                                                res[N].extend(res[key])
                                        # ����'ʱ
                                        else:
                                            res[N].extend(filter(lambda x: x != '��', fiset[item[i + 1]]))
                                            if '��' in fiset[item[i + 1]] and i + 1 == len(item) - 1:
                                                if bd[key] is False:
                                                    getfollow(key)
                                                res[N].extend(res[key])

                                    else:
                                        # Ϊ���ս��ʱ,��Ҫ�ų�����'
                                        if item[i + 1] != "'":
                                            res[N].append(item[i + 1])
                        # �÷��ս����'ʱ
                        else:
                            if i + 1 < len(item):
                                if item[i:i + 2] == N:
                                    if i + 1 is len(item) - 1:  # N����ʽ�����ұ�
                                        if bd[key] is False and key != N:
                                            getfollow(key)
                                        res[N].extend(res[key])
                                    else:  # �������ұ�
                                        # ��һ��Ϊ���ս��
                                        if item[i + 2] in string.ascii_uppercase:
                                            # �÷��ս��������'
                                            if i + 3 < len(item) and item[i + 3] == "'":
                                                res[N].extend(filter(lambda x: x != '��', fiset[item[i + 2:i + 4]]))
                                                # ���ս���������ұ�ʱ
                                                if '��' in fiset[item[i + 2:i + 4]] and i + 3 == len(item) - 1:
                                                    if bd[key] is False:
                                                        getfollow(key)
                                                    res[N].extend(res[key])
                                            # �÷��ս������'
                                            else:
                                                res[N].extend(filter(lambda x: x != '��', fiset[item[i + 2]]))
                                                # ���ս���������ұ�ʱ
                                                if '��' in fiset[item[i + 2]] and i + 2 == len(item) - 1:
                                                    if bd[key] is False:
                                                        getfollow(key)
                                                    res[N].extend(res[key])
                                        # ��һ��Ϊ�ս��
                                        else:
                                            res[N].append(item[i + 2])
            bd[N] = True

        res = dict()  # ��ŷ��ս����FOLLOW�����ֵ�,��Ϊ���ս��,ֵΪ�÷��ս����follow���ļ���
        bd = dict()
        for key in gramset.keys():
            res[key] = []
            bd[key] = False
        res[b].append('#')
        for key in gramset.keys():
            if bd[key] is False:
                getfollow(key)
        for key in gramset.keys():  # ���ֵ��е�ֵ���ʹ��б�ת�ɼ���,ȥ������ͬ��Ԫ��
            res[key] = list(set(res[key]))
            # if "'" in res[key]:
            #     res[key].remove("'")
        # print(f'followset:{res}')
        return res

    @staticmethod
    def prelist(gramset: dict, fiset: dict, follset: dict):  # ����Ԥ���
        nter = []  # ���ս���б�
        ter = []  # �ս��(��#)�б�
        for key in gramset.keys():
            nter.append(key)
        for key in fiset.keys():
            ter.extend(filter(lambda x: x != '��', fiset[key]))
        for key in follset.keys():
            ter.extend(follset[key])
            ter = list(set(ter))  # ȥ���ս���б���ͬ��
        ntdic = dict()
        tedic = dict()
        for i in range(len(nter)):
            ntdic[nter[i]] = i
        for i in range(len(ter)):
            tedic[ter[i]] = i
        res = []
        for i in ntdic.keys():  # ���ս��
            temp = []
            for j in tedic.keys():  # �ս��
                for n in range(len(gramset[i])):
                    # �ս����i����ʽ�ĵ�һ���ַ���first����
                    if gramset[i][n][0] in string.ascii_uppercase and j in fiset[gramset[i][n][0]]:
                        temp.append(gramset[i][n])
                        break
                    # �ս����i����ʽ�ĵ�һ���ַ�ʱ
                    elif gramset[i][n][0] not in string.ascii_uppercase and j is gramset[i][n][0]:
                        temp.append(gramset[i][n])
                        break
                    # �ս����ȡ��ʱ�����㴦��i��follow����
                    elif gramset[i][n][0] == '��' and j in follset[i]:
                        temp.append('��')
                        break
                    # ֱ�����һ������ʽҲ������������������ʱ������ΪError
                    if n == len(gramset[i]) - 1:
                        temp.append('Error')
            res.append(temp)
        # �������Ϊ��ӡ������ĸ�ʽ
        print(tedic)
        print(ntdic)
        print('Ԥ�����������:')
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
        self.root.title("LL(1)�ķ�������")

        label1 = tk.Label(self.root, text="�������ķ����ļ���ַ")
        label1.pack()

        frame1 = tk.Frame(self.root)
        frame1.pack()

        label2 = tk.Label(frame1, text="������Ҫ�������ķ�")
        label2.pack(side=tk.LEFT)

        self.text_box = tk.Entry(frame1)
        self.text_box.pack(side=tk.LEFT)

        button = tk.Button(self.root, text="�����ķ�", command=self.analyze_grammar)
        button.pack()

        self.root.mainloop()

    def analyze_grammar(self):
        # ������ʵ�ְ�ť�����Ĳ���
        SecondWindows(self.text_box.get())


class SecondWindows:
    def __init__(self, filename: str):
        root = tk.Tk()
        root.geometry(f"1000x600+{root.winfo_screenwidth() // 2 - 500}"
                      f"+{root.winfo_screenheight() // 2 - 300}")
        root.title('LL(1)����')
        # ��һ������������ķ�,first��,follow����Ԥ���
        frame1 = tk.Frame(root)
        frame3 = tk.Frame(frame1)
        frame3.pack()
        frame4 = tk.Frame(frame1)
        frame4.pack()
        frame5 = tk.Frame(frame1)
        frame5.pack()

        frame1.grid(row=0, column=0)

        # �ķ����
        lbwenfa = tk.Label(frame3, text='�ķ�:')
        lbwenfa.pack()
        lbtext_areawenfa = scrolledtext.ScrolledText(frame3, wrap=tk.WORD, width=60, height=10)
        lbtext_areawenfa.pack()
        self.gramli, self.begin = Solution.loadfile(filename)
        for key in self.gramli.keys():
            st = '|'.join(self.gramli[key])
            lbtext_areawenfa.insert(tk.END, f'{key}->{st}\n')
        lbtext_areawenfa.config(state="disabled")

        lbwenfa1 = tk.Label(frame3,text="������ݹ�:")
        lbwenfa1.pack()
        lbtext_areawenfa1 = scrolledtext.ScrolledText(frame3, wrap=tk.WORD, width=60, height=10)
        lbtext_areawenfa1.pack()
        self.gramli = Solution.eliminate_left_recursion(self.gramli)
        for key in self.gramli.keys():
            st = '|'.join(self.gramli[key])
            lbtext_areawenfa1.insert(tk.END, f'{key}->{st}\n')
        lbtext_areawenfa1.config(state="disabled")


        # First��Follow�����
        frame6 = tk.Frame(frame4)
        frame7 = tk.Frame(frame4)
        frame6.grid(row=0, column=0)
        frame7.grid(row=0, column=1)
        lbfirst = tk.Label(frame6, text='First��')
        lbfirst.pack()
        lbtext_areafirst = scrolledtext.ScrolledText(frame6, wrap=tk.WORD, width=30, height=10)
        lbtext_areafirst.pack()
        self.fistset = Solution.getfistset(self.gramli)
        for key in self.fistset.keys():
            st = ','.join(self.fistset[key])
            lbtext_areafirst.insert(tk.END, f'FIRST({key}) = {st}\n')
        lbtext_areafirst.config(state="disabled")
        lbfollow = tk.Label(frame7, text='Follow��')
        lbfollow.pack()
        lbtext_areafollow = scrolledtext.ScrolledText(frame7, wrap=tk.WORD, width=30, height=10)
        lbtext_areafollow.pack()
        self.followset = Solution.getfollowset(self.gramli, self.fistset, self.begin)
        for key in self.followset.keys():
            st = ','.join(self.followset[key])
            lbtext_areafollow.insert(tk.END, f'Follow({key}) = {st}\n')
        lbtext_areafollow.config(state="disabled")

        # Ԥ�����
        lbpreli = tk.Label(frame5, text='Ԥ���')
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

        # �ڶ���������������봮�͹���
        frame2 = tk.Frame(root)
        frame2.grid(row=0, column=1, sticky="nsew")
        # ���봮
        frame8 = tk.Frame(frame2)
        frame8.pack()
        lbshuru = tk.Label(frame8, text='�����ַ���:')
        lbshuru.pack(side=tk.LEFT)
        self.lbtext_box = tk.Entry(frame8)
        self.lbtext_box.pack(side=tk.LEFT)
        buton = tk.Button(frame2, text='ȷ��', command=self.startdipose)
        buton.pack()
        # ����
        lbpro = tk.Label(frame2, text='����')
        lbpro.pack()
        self.progress = scrolledtext.ScrolledText(frame2, wrap=tk.WORD, width=60)
        self.progress.pack()
        self.progress.insert(tk.END, f'����    ����ջ    ���봮    ���ñ��ʽ    \n')

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
            if top in ntdic.keys():  # ջ�������Ƿ��ս��
                if lis[ntdic[top]][tdic[insrt[0]]] != 'Error' and lis[ntdic[top]][tdic[insrt[0]]] != '��':
                    li = lis[ntdic[top]][tdic[insrt[0]]][::-1]
                    i = 0
                    while (i < len(li)):
                        if li[i] == "'" and i + 1 < len(li):
                            # 'Eת��E'��ջ
                            stack.append(li[i:i + 2][::-1])
                            i += 2
                        else:
                            stack.append(li[i])
                            i += 1
                    self.progress.insert(tk.END, f'{step}    {stack}    {insrt}    '
                                                 f'{top}->{lis[ntdic[top]][tdic[insrt[0]]]}\n')
                    step += 1
                    continue
                elif lis[ntdic[top]][tdic[insrt[0]]] == '��':  # ���Ԥ���Ǧ�,����Ҫ��ջ����
                    self.progress.insert(tk.END, f'{step}    {stack}    {insrt}    '
                                                 f'{top}->��\n')
                    step += 1
                    continue
                else:
                    self.progress.insert(tk.END, f'{step}    {stack}    {insrt}    '
                                                 f'Error')
                    break
            else:  # ջ���������ս��
                if top == insrt[0]:  # ջ���������һ���ַ�ƥ��
                    if top == '#':  # ƥ���������ַ�
                        break
                    else:
                        insrt = insrt[1:]
                        self.progress.insert(tk.END, f'{step}    {stack}    {insrt}    \n')
                        step += 1
                        continue
                else:  # ջ�����Ų�ƥ��
                    self.progress.insert(tk.END, f'{step}    {stack}    {insrt}    '
                                                 f'Error\n')
                    break


win = FirstWindows()

