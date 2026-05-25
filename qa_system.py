import tkinter as tk
from tkinter import scrolledtext
import jieba

# AI基础知识问答库
qa_db = {
    "什么是人工智能": "人工智能（AI）是计算机科学的一个分支，致力于创建能够模拟人类智能行为的系统，包括学习、推理、感知和决策等能力。",
    "人工智能的发展历史": "人工智能起源于1956年达特茅斯会议，经历了多次发展浪潮，从早期的专家系统到如今的深度学习，经历了低谷与复兴的循环。",
    "Python在人工智能中的作用": "Python因其简洁的语法、丰富的库生态（如NumPy、TensorFlow、PyTorch）和活跃的社区，成为人工智能领域最主流的编程语言。",
    "机器学习和深度学习的区别": "机器学习是让计算机从数据中学习规律的方法总称，深度学习是其子集，使用多层神经网络自动提取特征，适合处理图像、语音等复杂任务。",
    "什么是监督学习": "监督学习是用带标签的数据训练模型，让模型学会输入到输出的映射关系，常见算法有线性回归、决策树、支持向量机等。",
    "什么是无监督学习": "无监督学习在没有标签的数据中发现隐藏的结构和模式，主要用于聚类和降维，如K-means聚类和主成分分析。",
    "什么是强化学习": "强化学习让智能体通过与环境交互来学习策略，根据获得的奖励或惩罚不断调整行为，应用于游戏AI和机器人控制。",
    "神经网络的基本结构": "神经网络由输入层、隐藏层和输出层组成，每个神经元接收输入并加权求和后通过激活函数产生输出，多层叠加形成深度网络。",
    "什么是自然语言处理": "自然语言处理（NLP）让计算机理解和生成人类语言，应用包括机器翻译、情感分析、文本摘要和智能问答等。",
    "计算机视觉的应用": "计算机视觉让机器从图像和视频中提取信息，应用于人脸识别、自动驾驶、医学影像分析和工业质检等场景。",
    "什么是大语言模型": "大语言模型（LLM）是基于海量文本数据训练的深度学习模型，如GPT和BERT，能理解和生成自然语言文本，是目前AI领域的核心技术。",
    "什么是过拟合": "过拟合是模型在训练数据上表现很好但在新数据上表现差的现象，通常因为模型太复杂或训练数据太少，可以通过正则化和数据增强来缓解。",
    "什么是梯度下降": "梯度下降是一种优化算法，沿着损失函数梯度的反方向迭代更新参数，使损失逐步减小，是训练神经网络最基本的方法。",
    "什么是损失函数": "损失函数衡量模型预测值与真实值之间的差距，常见的有均方误差（MSE）用于回归、交叉熵损失用于分类。",
    "常见的激活函数": "常见的激活函数有Sigmoid（输出0到1）、ReLU（正数输出本身，负数输出0）、Tanh（输出-1到1），它们给网络引入非线性能力。",
    "什么是数据增强": "数据增强通过对训练数据进行变换（如翻转、旋转、裁剪）来扩充数据集，有效防止过拟合并提升模型的泛化能力。",
    "AI伦理问题有哪些": "AI伦理问题包括算法偏见、隐私泄露、失业影响、自主武器和深度伪造等，需要在技术发展的同时建立规范和监管。",
}

# 中文的停用词表，分词后要把这些过滤掉
stop_words = {"的", "是", "在", "有", "和", "与", "了", "吗", "什么", "怎么", "如何",
              "哪些", "一个", "能", "会", "可以", "都", "被", "把", "让",
              "等", "这", "那", "它", "其", "从", "到", "对", "上", "下", "中",
              "做", "用", "关于", "包括", "比较", "以及", "通过", "进行", "分别",
              "你", "我", "他", "请", "问", "告诉", "解释", "介绍", "说说"}


def build_keyword_index():
    q_keywords = {}
    kw_to_qs = {}

    for q in qa_db:
        words = jieba.lcut(q)
        kws = set()
        for w in words:
            w = w.strip()
            if len(w) >= 2 and w not in stop_words:
                kws.add(w)
        q_keywords[q] = kws
        # 反向索引，哪个关键词对应哪些问题
        for kw in kws:
            if kw not in kw_to_qs:
                kw_to_qs[kw] = []
            kw_to_qs[kw].append(q)

    return q_keywords, kw_to_qs


def find_best_match(user_input, q_keywords):
    # 把用户输入也分词、过滤
    words = jieba.lcut(user_input)
    user_kws = set()
    for w in words:
        w = w.strip()
        if len(w) >= 2 and w not in stop_words:
            user_kws.add(w)

    best_q = None
    max_overlap = 0

    for q, kws in q_keywords.items():
        # 求交集，交集越大说明越匹配
        overlap = len(user_kws & kws)
        if overlap > max_overlap:
            max_overlap = overlap
            best_q = q

    if best_q and max_overlap > 0:
        return qa_db[best_q]
    return "抱歉，未找到相关答案，请尝试其他问题。"


class QAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI基础问答系统")
        self.root.geometry("750x560")
        self.root.resizable(False, False)

        self.q_keywords, self.kw_to_qs = build_keyword_index()
        self.history = []  # 用来记录用户提过的问题

        self.setup_ui()

    def setup_ui(self):
        # 最上面的标题
        title_frame = tk.Frame(self.root, bg="#4A90D9", height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="人工智能基础问答系统", font=("微软雅黑", 16, "bold"),
                 bg="#4A90D9", fg="white").pack(expand=True)

        # 中间聊天区域
        chat_frame = tk.Frame(self.root)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.chat_area = scrolledtext.ScrolledText(chat_frame, font=("微软雅黑", 11),
                                                    wrap=tk.WORD, state=tk.DISABLED,
                                                    bg="#F5F5F5", relief=tk.FLAT)
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        # 下面是输入框
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(input_frame, text="请输入问题：", font=("微软雅黑", 11)).pack(side=tk.LEFT)
        self.entry = tk.Entry(input_frame, font=("微软雅黑", 12), width=40)
        self.entry.pack(side=tk.LEFT, padx=(5, 10), ipady=4)
        self.entry.bind("<Return>", lambda e: self.on_ask())

        tk.Button(input_frame, text="提问", font=("微软雅黑", 11), bg="#4A90D9", fg="white",
                  width=6, command=self.on_ask).pack(side=tk.LEFT, padx=3)
        tk.Button(input_frame, text="退出", font=("微软雅黑", 11), bg="#E74C3C", fg="white",
                  width=6, command=self.on_exit).pack(side=tk.LEFT, padx=3)

        # 最底下状态栏
        stats_frame = tk.Frame(self.root, bg="#E8E8E8", height=30)
        stats_frame.pack(fill=tk.X)
        stats_frame.pack_propagate(False)
        self.stats_label = tk.Label(stats_frame,
                                     text="知识库：" + str(len(qa_db)) + "个问题  |  已提问：0次",
                                     font=("微软雅黑", 9), bg="#E8E8E8", fg="#666")
        self.stats_label.pack(expand=True)

        self.add_msg("系统", "欢迎使用AI基础问答系统！输入问题开始提问，输入\"退出\"结束程序。")

    def add_msg(self, role, text):
        self.chat_area.config(state=tk.NORMAL)
        if role == "系统":
            self.chat_area.insert(tk.END, "【系统】" + text + "\n\n")
        elif role == "用户":
            self.chat_area.insert(tk.END, "  你：" + text + "\n")
        elif role == "AI":
            self.chat_area.insert(tk.END, "  AI：" + text + "\n\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def on_ask(self):
        question = self.entry.get().strip()
        if not question:
            return
        if question == "退出":
            self.on_exit()
            return

        # 记录到history列表
        self.history.append(question)
        self.add_msg("用户", question)
        self.entry.delete(0, tk.END)

        # 去匹配答案
        answer = find_best_match(question, self.q_keywords)
        self.add_msg("AI", answer)

        # 更新下面的计数
        self.stats_label.config(text="知识库：" + str(len(qa_db)) + "个问题  |  已提问：" + str(len(self.history)) + "次")

    def on_exit(self):
        if self.history:
            self.add_msg("系统", "本次对话共提问 " + str(len(self.history)) + " 次，感谢使用！")
        else:
            self.add_msg("系统", "感谢使用！")
        self.root.after(1500, self.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    app = QAApp(root)
    root.mainloop()
