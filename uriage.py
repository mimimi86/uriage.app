import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import datetime
import json

class データ管理:
    def __init__(self):
        self.商品一覧 = {}
        self.売上記録 = []
        self.経費記録 = []

    def 商品を追加(self, 名前, 価格):
        self.商品一覧[名前] = 価格

    def 売上を記録(self, 商品名, 個数):
        if 商品名 in self.商品一覧:
            self.売上記録.append({
                "商品": 商品名,
                "個数": 個数,
                "合計": self.商品一覧[商品名] * 個数
            })

    def 経費を記録(self, 支払者, 金額):
        self.経費記録.append({"支払者": 支払者, "金額": 金額})

    def 利益を計算(self):
        売上合計 = sum(i["合計"] for i in self.売上記録)
        経費合計 = sum(i["金額"] for i in self.経費記録)
        return 売上合計 - 経費合計

    def 保存する(self, タイトル):
        データ = {
            "商品一覧": self.商品一覧,
            "売上記録": self.売上記録,
            "経費記録": self.経費記録,
            "利益": self.利益を計算()
        }
        with open(f"{タイトル}.json", "w", encoding="utf-8") as f:
            json.dump(データ, f, ensure_ascii=False, indent=2)

    def PDF出力(self, タイトル):
        font_name = "IPAexGothic"
        font_path = os.path.join(os.path.dirname(__file__), "ipaexg.ttf")
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
        except Exception as e:
            print("フォント登録に失敗:", e)
            font_name = "Helvetica"  # フォールバック

        c = canvas.Canvas(f"{タイトル}.pdf")
        c.setFont(font_name, 12)
        c.drawString(100, 800, f"売上日報: {datetime.date.today()}")
        y = 770
        for item in self.売上記録:
            c.drawString(100, y, f"{item['商品']} x {item['個数']} = {item['合計']}円")
            y -= 20

        経費合計 = sum(i['金額'] for i in self.経費記録)
        c.drawString(100, y - 20, f"経費合計: {経費合計}円")
        c.drawString(100, y - 40, f"利益: {self.利益を計算()}円")
        y -= 80

        # 商品ごとの売上集計
        集計 = {}
        for item in self.売上記録:
            商品 = item['商品']
            if 商品 not in 集計:
                集計[商品] = {"個数": 0, "合計": 0}
            集計[商品]["個数"] += item["個数"]
            集計[商品]["合計"] += item["合計"]

        c.drawString(100, y, "＜商品別 集計＞")
        y -= 20
        for 商品, データ in 集計.items():
            c.drawString(100, y, f"{商品}: {データ['個数']}個、合計 {データ['合計']}円")
            y -= 20

        c.save()

class アプリ本体:
    def __init__(self, root):
        self.root = root
        self.root.title("売上管理アプリ")
        self.root.geometry("500x500")
        self.データ = データ管理()
        self.メニューバーを作成()
        self.メインフレーム = None
        self.売上入力画面()

    def メニューバーを作成(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        menubar.add_command(label="売上入力", command=self.売上入力画面)
        menubar.add_command(label="商品追加", command=self.商品追加画面)
        menubar.add_command(label="経費入力", command=self.経費入力画面)
        menubar.add_command(label="保存", command=self.保存処理)
        menubar.add_command(label="PDF出力", command=self.PDF出力画面)
        menubar.add_command(label="終了", command=self.終了処理)

    def フレームを切り替え(self):
        if self.メインフレーム:
            self.メインフレーム.destroy()
        self.メインフレーム = tk.Frame(self.root, padx=20, pady=20)
        self.メインフレーム.pack(fill=tk.BOTH, expand=True)

    def 売上入力画面(self):
        self.フレームを切り替え()
        tk.Label(self.メインフレーム, text="売上入力", font=("Helvetica", 14)).pack(pady=5)

        self.商品ウィジェット = {}

        for 商品名 in self.データ.商品一覧.keys():
            フレーム = tk.Frame(self.メインフレーム)
            フレーム.pack(anchor="w", pady=2)

            tk.Label(フレーム, text=商品名, width=15, anchor="w").pack(side="left")
            個数選択 = ttk.Combobox(フレーム, values=list(range(0, 21)), width=5, state="readonly")
            個数選択.set(0)
            個数選択.pack(side="left")

            self.商品ウィジェット[商品名] = 個数選択

        def 登録():
            登録数 = 0
            for 商品, 個数ボックス in self.商品ウィジェット.items():
                try:
                    個数 = int(個数ボックス.get())
                    if 個数 > 0:
                        self.データ.売上を記録(商品, 個数)
                        登録数 += 1
                except ValueError:
                    continue
            if 登録数:
                messagebox.showinfo("登録完了", f"{登録数}件の売上を登録しました。")
                for box in self.商品ウィジェット.values():
                    box.set(0)
            else:
                messagebox.showinfo("注意", "1つ以上の個数を選択してください。")

        tk.Button(self.メインフレーム, text="会計", command=登録, bg="#4CAF50", fg="white", font=("Helvetica", 12)).pack(pady=10)

    def 商品追加画面(self):
        self.フレームを切り替え()
        tk.Label(self.メインフレーム, text="商品追加", font=("Helvetica", 14)).pack(pady=5)
        tk.Label(self.メインフレーム, text="商品名").pack()
        商品名 = tk.Entry(self.メインフレーム)
        商品名.pack(pady=5)
        tk.Label(self.メインフレーム, text="価格").pack()
        価格 = tk.Entry(self.メインフレーム)
        価格.pack(pady=5)

        def 追加():
            try:
                if 商品名.get() == "":
                    messagebox.showerror("エラー", "商品名を入力してください。")
                    return
                self.データ.商品を追加(商品名.get(), int(価格.get()))
                messagebox.showinfo("完了", "商品を追加しました。")
                商品名.delete(0, tk.END)
                価格.delete(0, tk.END)
            except Exception:
                messagebox.showerror("エラー", "価格は数値で入力してください")

        tk.Button(self.メインフレーム, text="追加", command=追加, bg="#2196F3", fg="white", font=("Helvetica", 12)).pack(pady=10)

    def 経費入力画面(self):
        self.フレームを切り替え()
        tk.Label(self.メインフレーム, text="経費入力", font=("Helvetica", 14)).pack(pady=5)
        tk.Label(self.メインフレーム, text="支払者").pack()
        支払者 = tk.Entry(self.メインフレーム)
        支払者.pack(pady=5)
        tk.Label(self.メインフレーム, text="金額").pack()
        金額 = tk.Entry(self.メインフレーム)
        金額.pack(pady=5)

        def 登録():
            try:
                if 支払者.get() == "":
                    messagebox.showerror("エラー", "支払者を入力してください。")
                    return
                self.データ.経費を記録(支払者.get(), int(金額.get()))
                messagebox.showinfo("完了", "経費を登録しました。")
                支払者.delete(0, tk.END)
                金額.delete(0, tk.END)
            except Exception:
                messagebox.showerror("エラー", "金額は数値で入力してください")

        tk.Button(self.メインフレーム, text="登録", command=登録, bg="#FF5722", fg="white", font=("Helvetica", 12)).pack(pady=10)

    def 保存処理(self):
        タイトル = simpledialog.askstring("保存", "保存タイトルを入力してください")
        if タイトル:
            self.データ.保存する(タイトル)
            messagebox.showinfo("保存完了", f"{タイトル}.json に保存しました。")

    def PDF出力画面(self):
        タイトル = simpledialog.askstring("PDF出力", "PDFファイル名を入力してください")
        if タイトル:
            try:
                self.データ.PDF出力(タイトル)
                messagebox.showinfo("PDF出力完了", f"{タイトル}.pdf を作成しました。")
            except Exception as e:
                messagebox.showerror("エラー", f"PDF出力に失敗しました。\n{e}")

    def 終了処理(self):
        if messagebox.askokcancel("終了", "アプリを終了しますか？"):
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    アプリ本体(root)
    root.mainloop()
