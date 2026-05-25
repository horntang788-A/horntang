import unittest
import os
import csv
from datetime import datetime

# 导入主程序里的类
from fashion_system import Clothing, DataReader, Wardrobe, Recommender, ResultExporter


class TestClothing(unittest.TestCase):

    def test_create(self):
        c = Clothing("C001", "白色T恤", "上衣", "白色", "休闲", "M", "春夏", "4.5")
        self.assertEqual(c.cid, "C001")
        self.assertEqual(c.name, "白色T恤")
        self.assertEqual(c.category, "上衣")
        self.assertEqual(c.color, "白色")
        self.assertEqual(c.rating, 4.5)

    def test_rating_float(self):
        c = Clothing("C002", "黑裤子", "下装", "黑色", "商务", "L", "四季", "4.2")
        self.assertIsInstance(c.rating, float)
        self.assertAlmostEqual(c.rating, 4.2)

    def test_str(self):
        c = Clothing("C001", "白色T恤", "上衣", "白色", "休闲", "M", "春夏", "4.5")
        s = str(c)
        self.assertIn("C001", s)
        self.assertIn("白色T恤", s)


class TestDataReader(unittest.TestCase):

    def setUp(self):
        # 每次测试前创建一个临时csv
        self.test_file = "test_data_temp.csv"
        with open(self.test_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["编号", "名称", "类别", "颜色", "风格", "尺码", "季节", "评分"])
            writer.writerow(["T001", "测试上衣", "上衣", "白色", "休闲", "M", "春夏", "4.5"])
            writer.writerow(["T002", "测试裤子", "下装", "黑色", "商务", "L", "四季", "4.2"])
            writer.writerow(["T003", "测试外套", "外套", "灰色", "运动", "XL", "秋冬", "3.8"])

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_read(self):
        reader = DataReader(self.test_file)
        items = reader.read()
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].cid, "T001")
        self.assertEqual(items[1].name, "测试裤子")
        self.assertEqual(items[2].rating, 3.8)

    def test_file_not_found(self):
        reader = DataReader("不存在的文件.csv")
        items = reader.read()
        self.assertEqual(len(items), 0)

    def test_read_all_columns(self):
        reader = DataReader(self.test_file)
        items = reader.read()
        c = items[1]
        self.assertEqual(c.cid, "T002")
        self.assertEqual(c.category, "下装")
        self.assertEqual(c.color, "黑色")
        self.assertEqual(c.style, "商务")


class TestWardrobe(unittest.TestCase):

    def setUp(self):
        self.w = Wardrobe()
        self.w.add(Clothing("A1", "白T恤", "上衣", "白色", "休闲", "M", "春夏", "4.5"))
        self.w.add(Clothing("A2", "黑裤子", "下装", "黑色", "商务", "L", "四季", "4.2"))
        self.w.add(Clothing("A3", "灰外套", "外套", "灰色", "运动", "XL", "秋冬", "3.8"))
        self.w.add(Clothing("A4", "白鞋", "鞋", "白色", "休闲", "42", "四季", "4.3"))
        self.w.add(Clothing("A5", "蓝衬衫", "上衣", "蓝色", "商务", "M", "春秋", "4.6"))

    def test_add(self):
        self.assertEqual(len(self.w.get_all()), 5)

    def test_remove(self):
        self.w.remove("A1")
        self.assertEqual(len(self.w.get_all()), 4)
        self.assertFalse(any(c.cid == "A1" for c in self.w.get_all()))

    def test_remove_not_exist(self):
        self.w.remove("XXX")
        self.assertEqual(len(self.w.get_all()), 5)

    def test_filter_category(self):
        result = self.w.filter_by(category="上衣")
        self.assertEqual(len(result), 2)
        for c in result:
            self.assertEqual(c.category, "上衣")

    def test_filter_style(self):
        result = self.w.filter_by(style="商务")
        self.assertEqual(len(result), 2)

    def test_filter_season(self):
        result = self.w.filter_by(season="春")
        # 春夏的A1和春秋的A5都应该匹配
        self.assertTrue(len(result) >= 2)

    def test_filter_all(self):
        result = self.w.filter_by(category="上衣", style="商务")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].cid, "A5")

    def test_stats(self):
        stats = self.w.stats()
        self.assertEqual(stats["上衣"], 2)
        self.assertEqual(stats["下装"], 1)
        self.assertEqual(stats["外套"], 1)
        self.assertEqual(stats["鞋"], 1)

    def test_get_styles(self):
        styles = self.w.get_styles()
        self.assertIn("休闲", styles)
        self.assertIn("商务", styles)
        self.assertIn("运动", styles)


class TestRecommender(unittest.TestCase):

    def setUp(self):
        self.w = Wardrobe()
        self.w.add(Clothing("R1", "白T恤", "上衣", "白色", "休闲", "M", "春夏", "4.5"))
        self.w.add(Clothing("R2", "蓝衬衫", "上衣", "蓝色", "商务", "M", "春秋", "4.6"))
        self.w.add(Clothing("R3", "黑裤子", "下装", "黑色", "休闲", "L", "四季", "4.2"))
        self.w.add(Clothing("R4", "灰裤子", "下装", "灰色", "运动", "M", "四季", "4.0"))
        self.w.add(Clothing("R5", "白鞋", "鞋", "白色", "休闲", "42", "四季", "4.3"))
        self.w.add(Clothing("R6", "黑靴", "鞋", "黑色", "商务", "42", "秋冬", "4.7"))
        self.w.add(Clothing("R7", "黑外套", "外套", "黑色", "街头", "L", "秋冬", "4.3"))
        self.rec = Recommender(self.w)

    def test_recommend_basic(self):
        outfit = self.rec.recommend()
        # 至少应该有上衣+下装+鞋
        self.assertIn("上衣", outfit)
        self.assertIn("下装", outfit)
        self.assertIn("鞋", outfit)

    def test_recommend_by_style(self):
        items = self.rec.recommend_by_style("休闲")
        for item in items:
            self.assertEqual(item.style, "休闲")
        self.assertTrue(len(items) <= 5)

    def test_recommend_winter(self):
        # 冬天应该包含外套
        outfit = self.rec.recommend(season="冬")
        self.assertIn("外套", outfit)

    def test_recommend_with_color(self):
        outfit = self.rec.recommend(color="白色")
        # 首选白色的上衣应该被选中
        self.assertEqual(outfit["上衣"].color, "白色")

    def test_recommend_similar(self):
        shirt = Clothing("R1", "白T恤", "上衣", "白色", "休闲", "M", "春夏", "4.5")
        similar = self.rec.recommend_similar(shirt)
        # 结果不应包含自身
        for s in similar:
            self.assertNotEqual(s.cid, "R1")
        self.assertTrue(len(similar) <= 5)


class TestResultExporter(unittest.TestCase):

    def setUp(self):
        self.outfit = {
            "上衣": Clothing("E1", "白T恤", "上衣", "白色", "休闲", "M", "春夏", "4.5"),
            "下装": Clothing("E2", "黑裤子", "下装", "黑色", "商务", "L", "四季", "4.2"),
            "鞋": Clothing("E3", "白鞋", "鞋", "白色", "休闲", "42", "四季", "4.3"),
        }
        self.txt_file = "test_export_temp.txt"
        self.csv_file = "test_export_temp.csv"

    def tearDown(self):
        for f in [self.txt_file, self.csv_file]:
            if os.path.exists(f):
                os.remove(f)

    def test_export_txt(self):
        ResultExporter.export_txt(self.outfit, self.txt_file)
        self.assertTrue(os.path.exists(self.txt_file))
        with open(self.txt_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("白T恤", content)
        self.assertIn("黑裤子", content)
        self.assertIn("导出时间", content)

    def test_export_csv(self):
        ResultExporter.export_csv(self.outfit, self.csv_file)
        self.assertTrue(os.path.exists(self.csv_file))
        with open(self.csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)
        # 表头 + 3行数据 + 空行 + 时间行
        self.assertEqual(rows[0][0], "类别")
        self.assertEqual(rows[1][0], "上衣")
        self.assertEqual(rows[2][0], "下装")
        self.assertEqual(rows[3][0], "鞋")


if __name__ == "__main__":
    unittest.main()
