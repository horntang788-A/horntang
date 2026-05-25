import csv
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime

# 服装数据模型
class Clothing:
    def __init__(self, cid, name, category, color, style, size, season, rating):
        self.cid = cid
        self.name = name
        self.category = category      # 上衣/下装/外套/鞋/配饰
        self.color = color
        self.style = style            # 休闲/商务/运动/街头
        self.size = size
        self.season = season          # 春夏/秋冬/四季/春/夏/秋/冬/春秋/春夏
        self.rating = float(rating)

    def __str__(self):
        return self.cid + " " + self.name + " [" + self.category + "/" + self.color + "/" + self.style + "] " + str(self.rating) + "分"


# 数据读取
class DataReader:
    def __init__(self, filepath):
        self.filepath = filepath

    def read(self):
        # 读csv文件，返回Clothing列表
        clothes = []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    c = Clothing(
                        row["编号"], row["名称"], row["类别"],
                        row["颜色"], row["风格"], row["尺码"],
                        row["季节"], row["评分"]
                    )
                    clothes.append(c)
        except FileNotFoundError:
            print("找不到文件:" + self.filepath)
        except Exception as e:
            print("读取出错:" + str(e))
        return clothes


# 衣橱管理
class Wardrobe:
    def __init__(self):
        self.items = []

    def add(self, clothing):
        self.items.append(clothing)

    def remove(self, cid):
        self.items = [c for c in self.items if c.cid != cid]

    def get_all(self):
        return self.items

    def filter_by(self, category=None, color=None, style=None, season=None):
        result = self.items
        if category:
            result = [c for c in result if c.category == category]
        if color:
            result = [c for c in result if c.color == color]
        if style:
            result = [c for c in result if c.style == style]
        if season:
            result = [c for c in result if self._season_match(c.season, season)]
        return result

    def _season_match(self, item_season, target):
        # 判断服装季节是否匹配目标季节
        if item_season == "四季":
            return True
        return target in item_season

    def stats(self):
        # 各类别数量统计
        cats = {}
        for c in self.items:
            cats[c.category] = cats.get(c.category, 0) + 1
        return cats

    def get_categories(self):
        return list(set(c.category for c in self.items))

    def get_styles(self):
        return list(set(c.style for c in self.items))

    def get_colors(self):
        return list(set(c.color for c in self.items))


# 颜色搭配规则，预设一些比较安全的搭配方案
COLOR_RULES = {
    "白色": ["黑色", "蓝色", "灰色", "深蓝色", "卡其色", "棕色"],
    "黑色": ["白色", "灰色", "红色", "蓝色", "藏蓝色"],
    "蓝色": ["白色", "灰色", "深蓝色", "黑色"],
    "灰色": ["白色", "黑色", "蓝色", "军绿色"],
    "红色": ["黑色", "白色", "灰色"],
    "藏蓝色": ["白色", "浅蓝色", "米色"],
    "卡其色": ["白色", "蓝色", "黑色"],
    "棕色": ["白色", "米色", "藏蓝色", "黑色"],
    "军绿色": ["黑色", "白色", "灰色"],
    "米色": ["藏蓝色", "黑色", "白色", "棕色"],
    "驼色": ["黑色", "白色", "灰色", "藏蓝色"],
    "银色": ["黑色", "白色", "灰色", "蓝色"],
}

# 评分权重，颜色搭配合不合规就不选
STYLE_PRIORITY = {
    "商务": 0.3,
    "休闲": 0.25,
    "运动": 0.2,
    "街头": 0.25,
}


# 推荐算法
class Recommender:
    def __init__(self, wardrobe):
        self.wardrobe = wardrobe

    def recommend(self, style=None, season=None, color=None):
        # 根据用户偏好推荐一套搭配
        pool = self.wardrobe.filter_by(style=style, season=season)
        if not pool:
            pool = self.wardrobe.get_all()

        outfit = {}
        # 按类别各挑一个，组成一套搭配
        target_categories = ["上衣", "下装", "鞋"]
        # 如果是秋冬，加个外套
        if season and "冬" in season:
            target_categories.append("外套")

        first_color = color  # 用户选的颜色，用于判断搭配

        for i, cat in enumerate(target_categories):
            candidates = [c for c in pool if c.category == cat]
            if not candidates:
                continue

            if first_color:
                # 用户指定了颜色，优先选该颜色的
                same_color = [c for c in candidates if c.color == first_color]
                if same_color and (i == 0 or same_color[0].rating >= 4.0):
                    candidates = same_color
                elif i > 0:
                    # 后面的单品颜色要和第一个搭配
                    ok = []
                    for c in candidates:
                        if first_color in COLOR_RULES.get(c.color, []) or c.color in COLOR_RULES.get(first_color, []):
                            ok.append(c)
                    if ok:
                        candidates = ok

            # 按评分排序，选最高的
            candidates.sort(key=lambda x: x.rating, reverse=True)
            outfit[cat] = candidates[0]

            if outfit[cat]:
                first_color = outfit[cat].color

        # 再挑个配饰
        acc_candidates = [c for c in pool if c.category == "配饰"]
        if acc_candidates:
            acc_candidates.sort(key=lambda x: x.rating, reverse=True)
            outfit["配饰"] = acc_candidates[0]

        return outfit

    def recommend_by_style(self, style):
        # 单纯按风格推荐，返回top5
        items = self.wardrobe.filter_by(style=style)
        items.sort(key=lambda x: x.rating, reverse=True)
        return items[:5]

    def recommend_similar(self, clothing):
        # 推荐和某件衣服相似的（同风格+颜色搭配）
        items = self.wardrobe.filter_by(style=clothing.style)
        result = []
        for c in items:
            if c.cid != clothing.cid:
                score = 0
                if c.category != clothing.category:
                    score += 2  # 不同类别才适合搭配
                if clothing.color in COLOR_RULES.get(c.color, []) or c.color in COLOR_RULES.get(clothing.color, []):
                    score += 3
                if c.color == clothing.color:
                    score += 1  # 同色也算可以
                score += c.rating
                result.append((c, score))
        result.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in result[:5]]


# 结果导出
class ResultExporter:
    @staticmethod
    def export_txt(outfit, filepath):
        # 把推荐结果写到txt文件
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = ["AI智能服装搭配推荐结果", "导出时间: " + now, "=" * 40, ""]
        for cat, c in outfit.items():
            lines.append(cat + ": " + c.cid + " " + c.name)
            lines.append("  颜色=" + c.color + " 风格=" + c.style + " 尺码=" + c.size + " 评分=" + str(c.rating))
            lines.append("")
        lines.append("=" * 40)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    @staticmethod
    def export_csv(outfit, filepath):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["类别", "编号", "名称", "颜色", "风格", "尺码", "季节", "评分"])
            for cat, c in outfit.items():
                writer.writerow([cat, c.cid, c.name, c.color, c.style, c.size, c.season, c.rating])
            writer.writerow([])
            writer.writerow(["导出时间", now])


# GUI界面
class FashionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI智能服装搭配推荐系统")
        self.root.geometry("900x650")
        self.root.resizable(False, False)

        # 初始化数据
        reader = DataReader("clothing_data.csv")
        self.wardrobe = Wardrobe()
        for c in reader.read():
            self.wardrobe.add(c)
        self.recommender = Recommender(self.wardrobe)
        self.last_outfit = {}

        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        # 顶部标题
        top = tk.Frame(self.root, bg="#2C3E50", height=48)
        top.pack(fill=tk.X)
        top.pack_propagate(False)
        tk.Label(top, text="AI智能服装搭配推荐系统", font=("微软雅黑", 15, "bold"),
                 bg="#2C3E50", fg="white").pack(side=tk.LEFT, padx=20)

        # 主区域分左右
        main = tk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # 左边：筛选+推荐
        left = tk.Frame(main, width=260)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left.pack_propagate(False)

        tk.Label(left, text="偏好设置", font=("微软雅黑", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))

        # 风格选择
        tk.Label(left, text="风格:").pack(anchor=tk.W)
        self.style_var = tk.StringVar(value="全部")
        styles = ["全部"] + sorted(self.wardrobe.get_styles())
        self.style_combo = ttk.Combobox(left, textvariable=self.style_var, values=styles, state="readonly", width=20)
        self.style_combo.pack(fill=tk.X, pady=(0, 5))

        # 季节选择
        tk.Label(left, text="季节:").pack(anchor=tk.W)
        self.season_var = tk.StringVar(value="全部")
        seasons = ["全部", "春", "夏", "秋", "冬", "春秋", "春夏", "秋冬"]
        self.season_combo = ttk.Combobox(left, textvariable=self.season_var, values=seasons, state="readonly", width=20)
        self.season_combo.pack(fill=tk.X, pady=(0, 5))

        # 颜色选择
        tk.Label(left, text="首选颜色:").pack(anchor=tk.W)
        self.color_var = tk.StringVar(value="不限")
        colors = ["不限"] + sorted(self.wardrobe.get_colors())
        self.color_combo = ttk.Combobox(left, textvariable=self.color_var, values=colors, state="readonly", width=20)
        self.color_combo.pack(fill=tk.X, pady=(0, 10))

        # 按钮区
        btn_style = {"font": ("微软雅黑", 10), "width": 18, "height": 1}
        tk.Button(left, text="一键搭配推荐", bg="#27AE60", fg="white",
                  command=self._on_recommend, **btn_style).pack(pady=3)
        tk.Button(left, text="风格推荐 TOP5", bg="#2980B9", fg="white",
                  command=self._on_style_rec, **btn_style).pack(pady=3)
        tk.Button(left, text="导出推荐结果", bg="#F39C12", fg="white",
                  command=self._on_export, **btn_style).pack(pady=3)
        tk.Button(left, text="清空推荐", bg="#95A5A6", fg="white",
                  command=self._on_clear, **btn_style).pack(pady=3)

        # 衣橱统计
        tk.Label(left, text="", font=("微软雅黑", 1)).pack()
        tk.Label(left, text="衣橱统计", font=("微软雅黑", 11, "bold")).pack(anchor=tk.W)
        stats = self.wardrobe.stats()
        stat_text = "共" + str(len(self.wardrobe.get_all())) + "件\n"
        for cat, cnt in stats.items():
            stat_text += cat + ": " + str(cnt) + "件\n"
        tk.Label(left, text=stat_text, font=("微软雅黑", 9), justify=tk.LEFT).pack(anchor=tk.W)

        # 右边：列表+推荐结果
        right = tk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 上半部分：服装列表
        list_frame = tk.LabelFrame(right, text="全部服装", font=("微软雅黑", 10))
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        cols = ("编号", "名称", "类别", "颜色", "风格", "季节", "评分")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            w = 55 if col in ("编号", "类别", "颜色", "季节") else 70 if col == "评分" else 110
            self.tree.column(col, width=w, anchor=tk.CENTER)

        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # 下半部分：推荐结果
        rec_frame = tk.LabelFrame(right, text="推荐结果", font=("微软雅黑", 10))
        rec_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = scrolledtext.ScrolledText(rec_frame, font=("微软雅黑", 10),
                                                     wrap=tk.WORD, state=tk.DISABLED,
                                                     bg="#FAFAFA", height=8)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

    def _refresh_list(self):
        # 刷新服装列表
        self.tree.delete(*self.tree.get_children())
        for c in self.wardrobe.get_all():
            self.tree.insert("", tk.END, values=(
                c.cid, c.name, c.category, c.color, c.style, c.season, c.rating
            ))

    def _show_result(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state=tk.DISABLED)

    def _on_recommend(self):
        style = self.style_var.get()
        season = self.season_var.get()
        color = self.color_var.get()

        s = None if style == "全部" else style
        sn = None if season == "全部" else season
        cl = None if color == "不限" else color

        outfit = self.recommender.recommend(style=s, season=sn, color=cl)
        self.last_outfit = outfit

        if not outfit:
            self._show_result("没有找到合适的搭配，试试换个条件吧")
            return

        lines = ["【今日推荐搭配】\n"]
        total_score = 0
        for cat, c in outfit.items():
            lines.append(cat + ": " + c.name + " (" + c.color + "/" + c.style + ") " + str(c.rating) + "分")
            total_score += c.rating
        lines.append("\n搭配总评分: " + str(round(total_score / len(outfit), 1)) + " / 5.0")
        self._show_result("\n".join(lines))

    def _on_style_rec(self):
        style = self.style_var.get()
        if style == "全部":
            messagebox.showinfo("提示", "请先选择一个具体风格")
            return
        items = self.recommender.recommend_by_style(style)
        if not items:
            self._show_result("该风格暂无服装")
            return
        lines = ["【" + style + "风格 TOP5 推荐】\n"]
        for i, c in enumerate(items, 1):
            lines.append(str(i) + ". " + c.name + " [" + c.category + "/" + c.color + "] " + str(c.rating) + "分")
        self._show_result("\n".join(lines))

    def _on_export(self):
        if not self.last_outfit:
            messagebox.showinfo("提示", "请先获取推荐搭配再导出")
            return
        fname = "推荐结果_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"
        ResultExporter.export_txt(self.last_outfit, fname)
        messagebox.showinfo("导出成功", "文件已保存: " + fname)

    def _on_clear(self):
        self.last_outfit = {}
        self._show_result("")
        self.style_var.set("全部")
        self.season_var.set("全部")
        self.color_var.set("不限")


# 主入口
if __name__ == "__main__":
    root = tk.Tk()
    app = FashionApp(root)
    root.mainloop()
