# ocr_app.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import threading
import json
import os
import time
from datetime import datetime

# ==================== OCR类型中文映射表 ====================
OCR_TYPE_NAMES = {
    # 通用
    "GENERAL": "通用文字识别",
    "BILL_MIXING_AND_IDENTIFICATION": "票据混合识别",
    "SEAL_CHARACTER_RECOGNITION": "印章文字识别",
    "TABLE_RECOGNITION": "表格识别",
    # 证件类
    "ID_CARD": "大陆身份证",
    "BANK_CARD": "银行卡",
    "SOCIAL_SECURITY_CARD": "社保卡",
    "HOUSEHOLD_REGISTER": "户口本",
    "BIRTH_CERTIFICATE": "出生证明",
    "HK_MACAU_PASS": "港澳通行证",
    "TAIWAN_PASS": "台湾通行证",
    "TAIWAN_MAINLAND_PASS": "台湾居民来往大陆通行证",
    "HK_MAINLAND_PASS": "港澳居民来往内地通行证",
    "HONG_KONG_IDENTITY_CARD": "香港身份证",
    "PERMANENT_RESIDENCE_ID_CARD_FOR": "外国人永久居留身份证",
    "MARRIAGE_CERTIFICATE": "结婚证",
    "REAL_ESTATE_OWNERSHIP_CERTIFICAT": "不动产权证书",
    "FRONT_PAGE_OF_MOTOR_VEHICLE_DRIV": "机动车行驶证正页",
    "SECOND_SHEET_OF_MOTOR_VEHICLE_DR": "机动车行驶证副页",
    "MOTOR_VEHICLE_DRIVING_LICENSE": "机动车驾驶证",
    "MOTOR_VEHICLE_DRIVING_LICENSE_SU": "机动车驾驶证副页",
    "CHINESE_PASSPORT": "中国护照",
    # 学历类
    "ACADEMIC_CERTIFICATE": "学业证书",
    "ONLINE_VERIFICATION_REPORT_OF_HE": "学历证书电子注册备案表",
    "DIPLOMA": "毕业证",
    # 资质类
    "BUSINESS_LICENSE": "营业执照",
    "SOCIAL_ORG_REG": "社会团体法人登记证书",
    "TRADE_UNION_REG": "工会法人资格证书",
    "PRIVATE_NON_ENTERPRISE_REG": "民办非企业单位登记证书",
    "INSTITUTION_LEGAL_REG": "事业单位法人证书",
    "UNIFIED_SOCIAL_CREDIT_REG": "统一社会信用代码证书",
    "FOOD_BUSINESS_LICENSE": "食品经营许可证",
    "FOOD_PRODUCTION_LICENSE": "食品生产许可证",
    "HYGIENE_LICENSE": "卫生许可证",
    "FINANCIAL_LICENSE": "金融许可证",
    "FINANCIAL_INSTITUTION_CODE_CERT": "金融机构代码证",
    "PAYMENT_BUSINESS_LICENSE": "支付业务许可证",
    "ACCOUNT_OPENING_LICENSE": "开户许可证",
    "TRADEMARK_REGISTRATION_CERT": "商标注册证",
    "TAX_REGISTRATION_CERT": "税务登记证",
    "ORGANIZATION_CODE_CERT": "组织机构代码证",
    "UNIFIED_IDENTIFICATION_OF_FINANC": "金融机构统一社会信用代码证",
    # 发票类
    "VAT_INVOICE": "增值税发票",
    "VAT_TOLL_INVOICE": "增值税通行费发票",
    "VAT_ROLL_INVOICE": "增值税卷票",
    "TAXI_INVOICE": "出租车发票",
    "TRAIN_TICKET": "火车票",
    "AIRPORT_TICKET": "航空电子客票行程单",
    "VEHICLE_SALE_INVOICE": "机动车销售统一发票",
    "QUOTA_INVOICE": "定额发票",
    "TOLL_INVOICE": "过路过桥费发票",
    "MEDICAL_INVOICE": "医疗发票",
    "MEDICAL_INPATIENT_INVOICE": "医疗住院发票",
    "MEDICAL_EXPENSE_SETTLEMENT": "医疗费用结算单",
    "TAX_CERTIFICATE": "税收完税证明",
    "SHIP_TICKET": "船票",
    "NON_TAX_BILL": "非税票据",
    "GENERAL_MACHINE_INVOICE": "通用机打发票",
    "BUS_TICKET": "汽车票",
    "RIDE_HAILING_ITINERARY": "网约车行程单",
    # 金融类
    "UNIONPAY_POS_RECEIPT": "银联POS签购单",
    "BANK_DRAFT": "银行汇票",
    "BANK_ACCEPTANCE_BILL": "银行承兑汇票",
    "ELECTRONIC_BANK_ACCEPTANCE_BILL": "电子银行承兑汇票",
    "COMMERCIAL_ACCEPTANCE_BILL": "商业承兑汇票",
    "ELECTRONIC_COMMERCIAL_ACCEPTANCE": "电子商业承兑汇票",
    "BANK_CHECK": "银行支票",
    "BANK_RECEIPT": "银行回单",
    "DEPOSIT_SLIP": "存款凭条",
    "TELEGRAPHIC_TRANSFER_VOUCHER": "电汇凭证",
    "WITHDRAWAL_VOUCHER": "支款凭证",
    "MOBILE_PAYMENT_BILL": "移动支付账单",
    "FISCAL_AUTH_PAYMENT_VOUCHER": "财政授权支付凭证",
    "CUSTOMS_PAYMENT_RECEIPT": "海关缴款书",
    "CUSTOMS_DECLARATION": "海关报关单",
    # 贸易类
    "INTERNATIONAL_BILL": "国际账单",
    "COMMERCIAL_INVOICE": "商业发票",
    "CERTIFICATE_OF_ORIGIN": "原产地证书",
    "CARGO_TRANSPORT_INSURANCE": "货物运输保险单",
    "PACKING_LIST": "装箱单",
    "BILL_OF_LADING": "提单",
}

OCR_DISPLAY_TO_CODE = {name: code for code, name in OCR_TYPE_NAMES.items()}
OCR_DISPLAY_NAMES = list(OCR_TYPE_NAMES.values())


class KeyManager:
    """API密钥管理器"""
    def __init__(self):
        self.key_file = os.path.join(os.path.expanduser("~"), ".ocr_tool_keys.json")
        self.keys = {}
        self.load_keys()
    
    def load_keys(self):
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.keys = data.get('keys', {})
        except Exception as e:
            print(f"加载密钥失败: {e}")
            self.keys = {}
    
    def save_keys(self):
        try:
            with open(self.key_file, 'w', encoding='utf-8') as f:
                json.dump({'keys': self.keys}, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存密钥失败: {e}")
            return False
    
    def add_key(self, name, key):
        self.keys[name] = key
        return self.save_keys()
    
    def delete_key(self, name):
        if name in self.keys:
            del self.keys[name]
            return self.save_keys()
        return False
    
    def get_key(self, name):
        return self.keys.get(name, '')
    
    def get_key_names(self):
        return list(self.keys.keys())


class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR文档处理工具")
        self.root.geometry("950x800")
        
        self.api_base = "https://api.scnet.cn/api/llm/v1"
        self.key_manager = KeyManager()
        self.remember_key = tk.BooleanVar(value=False)
        
        # 默认输出目录
        self.default_output_dir = os.path.join(os.getcwd(), "output")
        self.output_dir = tk.StringVar(value=self.default_output_dir)
        os.makedirs(self.default_output_dir, exist_ok=True)
        
        self.create_widgets()
        self.load_last_key()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)  # 增加一行用于结果区
        
        # ========== API配置 ==========
        api_frame = ttk.LabelFrame(main_frame, text="API配置", padding="10")
        api_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        api_frame.columnconfigure(1, weight=1)
        
        ttk.Label(api_frame, text="密钥名称:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.key_name = tk.StringVar()
        self.key_combo = ttk.Combobox(api_frame, textvariable=self.key_name, width=30)
        self.key_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        self.key_combo.bind('<<ComboboxSelected>>', self.on_key_selected)
        
        key_btn_frame = ttk.Frame(api_frame)
        key_btn_frame.grid(row=0, column=2, columnspan=2, sticky=tk.W, pady=5)
        ttk.Button(key_btn_frame, text="新建", command=self.create_new_key).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(key_btn_frame, text="删除", command=self.delete_key).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(key_btn_frame, text="刷新", command=self.refresh_keys).pack(side=tk.LEFT)
        
        ttk.Label(api_frame, text="API密钥:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.api_key = tk.StringVar()
        self.api_entry = ttk.Entry(api_frame, textvariable=self.api_key, show="*", width=50)
        self.api_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
        
        self.show_key = tk.BooleanVar(value=False)
        self.show_key_checkbox = ttk.Checkbutton(
            api_frame, text="显示密钥", variable=self.show_key, command=self.toggle_key_visibility
        )
        self.show_key_checkbox.grid(row=1, column=2, sticky=tk.W)
        
        self.remember_checkbox = ttk.Checkbutton(
            api_frame, text="记住密钥", variable=self.remember_key, command=self.toggle_remember_key
        )
        self.remember_checkbox.grid(row=1, column=3, sticky=tk.W)
        
        # ========== 文件选择 ==========
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        self.file_path = tk.StringVar()
        ttk.Label(file_frame, text="文件路径:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.file_path).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="浏览", command=self.browse_file).grid(row=0, column=2)
        
        # ========== 输出目录选择 ==========
        output_frame = ttk.LabelFrame(main_frame, text="输出目录", padding="10")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="保存位置:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(output_frame, textvariable=self.output_dir).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(output_frame, text="浏览", command=self.browse_output_dir).grid(row=0, column=2)
        
        # ========== 功能选择 ==========
        func_frame = ttk.LabelFrame(main_frame, text="功能选择", padding="10")
        func_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.function_var = tk.StringVar(value="ocr")
        ttk.Radiobutton(func_frame, text="通用OCR识别", variable=self.function_var,
                       value="ocr", command=self.update_options).grid(row=0, column=0, padx=(0, 20))
        ttk.Radiobutton(func_frame, text="文档解析", variable=self.function_var,
                       value="parse", command=self.update_options).grid(row=0, column=1, padx=(0, 20))
        ttk.Radiobutton(func_frame, text="格式转换", variable=self.function_var,
                       value="convert", command=self.update_options).grid(row=0, column=2)
        
        # ========== 参数配置 ==========
        param_frame = ttk.LabelFrame(main_frame, text="参数配置", padding="10")
        param_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        param_frame.columnconfigure(1, weight=1)
        
        # OCR类型（中文）
        self.ocr_type_label = ttk.Label(param_frame, text="OCR类型:")
        self.ocr_type_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.ocr_type = tk.StringVar(value="通用文字识别")
        self.ocr_combo = ttk.Combobox(param_frame, textvariable=self.ocr_type,
                                     values=OCR_DISPLAY_NAMES, state="readonly", width=35)
        self.ocr_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 目标格式
        self.format_label = ttk.Label(param_frame, text="目标格式:")
        self.format_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.convert_format = tk.StringVar(value="docx")
        self.format_combo = ttk.Combobox(param_frame, textvariable=self.convert_format,
                                        values=["docx", "pptx"], state="readonly")
        self.format_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 高级选项（文档解析专用）
        self.parse_extra_label = ttk.Label(param_frame, text="高级选项:")
        self.parse_extra_label.grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        
        extra_frame = ttk.Frame(param_frame)
        extra_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.parse_extra_frame = extra_frame
        
        self.is_table_cls = tk.BooleanVar(value=False)
        self.is_doc_ori = tk.BooleanVar(value=False)
        self.enforce_seal = tk.BooleanVar(value=False)
        self.is_inline_formula = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(extra_frame, text="表格细分", variable=self.is_table_cls).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(extra_frame, text="方向矫正", variable=self.is_doc_ori).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(extra_frame, text="印章检测", variable=self.enforce_seal).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(extra_frame, text="行内公式", variable=self.is_inline_formula).pack(side=tk.LEFT)
        
        # 默认隐藏高级选项
        self.parse_extra_label.grid_remove()
        extra_frame.grid_remove()
        
        # ========== 操作按钮 ==========
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, pady=(10, 0))
        
        self.execute_btn = ttk.Button(button_frame, text="开始处理", command=self.execute_task)
        self.execute_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.clear_btn = ttk.Button(button_frame, text="清空结果", command=self.clear_result)
        self.clear_btn.pack(side=tk.LEFT)
        self.progress = ttk.Progressbar(button_frame, mode='indeterminate', length=200)
        self.progress.pack(side=tk.LEFT, padx=(20, 0))
        
        # ========== 结果展示 ==========
        result_frame = ttk.LabelFrame(main_frame, text="结果展示", padding="10")
        result_frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, height=20)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.update_options()
        self.refresh_keys()
    
    # ========== 密钥管理 ==========
    def load_last_key(self):
        config_file = os.path.join(os.path.expanduser("~"), ".ocr_tool_config.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    last_key_name = config.get('last_key_name', '')
                    remember = config.get('remember_key', False)
                    if remember and last_key_name:
                        key = self.key_manager.get_key(last_key_name)
                        if key:
                            self.key_name.set(last_key_name)
                            self.api_key.set(key)
                            self.remember_key.set(True)
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def save_config(self):
        config_file = os.path.join(os.path.expanduser("~"), ".ocr_tool_config.json")
        try:
            config = {
                'last_key_name': self.key_name.get(),
                'remember_key': self.remember_key.get()
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def toggle_key_visibility(self):
        self.api_entry.config(show='' if self.show_key.get() else '*')
    
    def toggle_remember_key(self):
        if self.remember_key.get():
            if self.key_name.get() and self.api_key.get().strip():
                self.key_manager.add_key(self.key_name.get(), self.api_key.get().strip())
                self.save_config()
                messagebox.showinfo("成功", "密钥已保存")
        else:
            self.save_config()
    
    def create_new_key(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新建密钥")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="密钥名称:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="API密钥:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        key_entry = ttk.Entry(dialog, width=30, show="*")
        key_entry.grid(row=1, column=1, padx=10, pady=10)
        
        def save_new_key():
            name = name_entry.get().strip()
            key = key_entry.get().strip()
            if not name or not key:
                messagebox.showerror("错误", "请填写完整的密钥信息")
                return
            if self.key_manager.add_key(name, key):
                self.refresh_keys()
                self.key_name.set(name)
                self.api_key.set(key)
                if self.remember_key.get():
                    self.save_config()
                messagebox.showinfo("成功", f"密钥 '{name}' 已保存")
                dialog.destroy()
            else:
                messagebox.showerror("错误", "保存密钥失败")
        
        ttk.Button(dialog, text="保存", command=save_new_key).grid(row=2, column=0, columnspan=2, pady=20)
    
    def delete_key(self):
        key_name = self.key_name.get()
        if not key_name:
            messagebox.showwarning("警告", "请选择要删除的密钥")
            return
        if messagebox.askyesno("确认", f"确定要删除密钥 '{key_name}' 吗？"):
            if self.key_manager.delete_key(key_name):
                self.refresh_keys()
                self.api_key.set("")
                self.key_name.set("")
                messagebox.showinfo("成功", "密钥已删除")
            else:
                messagebox.showerror("错误", "删除密钥失败")
    
    def refresh_keys(self):
        key_names = self.key_manager.get_key_names()
        self.key_combo['values'] = key_names
        if key_names and not self.key_name.get():
            self.key_name.set(key_names[0])
            self.on_key_selected()
    
    def on_key_selected(self, event=None):
        key_name = self.key_name.get()
        if key_name:
            key = self.key_manager.get_key(key_name)
            if key:
                self.api_key.set(key)
    
    # ========== 界面更新 ==========
    def update_options(self):
        func = self.function_var.get()
        if func == "ocr":
            self.ocr_type_label.grid()
            self.ocr_combo.grid()
            self.ocr_combo.config(state="readonly")
            self.format_label.grid_remove()
            self.format_combo.grid_remove()
            self.parse_extra_label.grid_remove()
            self.parse_extra_frame.grid_remove()
        elif func == "parse":
            # 隐藏OCR类型，因为文档解析固定使用DOC_PARING
            self.ocr_type_label.grid_remove()
            self.ocr_combo.grid_remove()
            self.format_label.grid_remove()
            self.format_combo.grid_remove()
            self.parse_extra_label.grid()
            self.parse_extra_frame.grid()
        else:  # convert
            self.ocr_type_label.grid_remove()
            self.ocr_combo.grid_remove()
            self.format_label.grid()
            self.format_combo.grid()
            self.parse_extra_label.grid_remove()
            self.parse_extra_frame.grid_remove()
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="选择文件",
            filetypes=[
                ("所有文件", "*.*"),
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                ("文档文件", "*.pdf *.doc *.docx *.txt *.md"),
                ("Office文件", "*.docx *.xlsx *.pptx")
            ]
        )
        if filename:
            size = os.path.getsize(filename) / (1024 * 1024)
            if size > 20:
                messagebox.showwarning("文件较大", f"文件大小 {size:.1f} MB，上传可能较慢，建议压缩后再试。")
            self.file_path.set(filename)
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)
    
    def execute_task(self):
        if not self.file_path.get():
            messagebox.showwarning("警告", "请先选择文件")
            return
        if not self.api_key.get().strip():
            messagebox.showwarning("警告", "请输入API密钥")
            return
        if self.remember_key.get() and self.key_name.get():
            self.key_manager.add_key(self.key_name.get(), self.api_key.get().strip())
            self.save_config()
        
        file_path = self.file_path.get()
        if not os.path.exists(file_path):
            messagebox.showerror("错误", "文件不存在")
            return
        
        # 确保输出目录存在
        output_dir = self.output_dir.get().strip()
        if not output_dir:
            output_dir = self.default_output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.execute_btn.config(state=tk.DISABLED)
        self.progress.start()
        thread = threading.Thread(target=self.process_task, args=(file_path, output_dir))
        thread.daemon = True
        thread.start()
    
    def get_headers(self):
        return {'Authorization': f'Bearer {self.api_key.get().strip()}'}
    
    def get_mime_type(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
            '.bmp': 'image/bmp', '.tiff': 'image/tiff', '.tif': 'image/tiff',
            '.gif': 'image/gif', '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.txt': 'text/plain', '.md': 'text/markdown',
            '.html': 'text/html', '.htm': 'text/html',
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    # ==================== 文件下载工具 ====================
    def download_files(self, urls, task_id, output_dir):
        """
        下载多个文件到指定目录，返回本地路径列表和内容摘要（仅对json/txt）
        """
        local_paths = []
        content_summary = ""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for idx, url in enumerate(urls):
            try:
                # 获取文件名
                # 先用head获取content-disposition
                try:
                    head_resp = requests.head(url, timeout=10)
                    content_disposition = head_resp.headers.get('content-disposition', '')
                except:
                    content_disposition = ''
                
                if 'filename=' in content_disposition:
                    # 解析文件名（简单处理）
                    fname = content_disposition.split('filename=')[-1].strip('"')
                    # 如果包含 *UTF-8'' 则提取
                    if "filename*=" in content_disposition:
                        # 取最后一个 filename* 的值
                        parts = content_disposition.split(';')
                        for part in parts:
                            if 'filename*=' in part:
                                raw = part.split('filename*=')[-1].strip()
                                if raw.startswith("UTF-8''"):
                                    fname = raw[7:]
                                break
                else:
                    # 从URL中提取
                    fname = os.path.basename(url.split('?')[0])
                    if not fname:
                        fname = f"result_{idx+1}"
                
                # 生成本地文件名（加时间戳和任务ID前缀）
                base, ext = os.path.splitext(fname)
                if not ext:
                    ext = '.bin'
                safe_fname = f"{task_id}_{timestamp}_{idx+1}{ext}"
                local_path = os.path.join(output_dir, safe_fname)
                
                # 下载文件
                download_headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                with requests.get(url, headers=download_headers, stream=True, timeout=60) as r:
                    r.raise_for_status()
                    with open(local_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                local_paths.append(local_path)
                
                # 如果是json或txt，读取内容用于展示
                if ext.lower() in ['.json', '.txt']:
                    try:
                        with open(local_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if ext.lower() == '.json':
                                # 格式化json
                                try:
                                    data = json.loads(content)
                                    content_summary += f"\n--- 文件 {idx+1} ({fname}) 内容 ---\n"
                                    content_summary += json.dumps(data, indent=2, ensure_ascii=False)
                                except:
                                    content_summary += f"\n--- 文件 {idx+1} ({fname}) 内容 ---\n{content}"
                            else:
                                content_summary += f"\n--- 文件 {idx+1} ({fname}) 内容 ---\n{content}"
                    except Exception as e:
                        content_summary += f"\n无法读取 {fname} 内容: {e}"
            except Exception as e:
                local_paths.append(f"下载失败: {url} - {str(e)}")
        
        return local_paths, content_summary
    
    # ==================== 文档解析JSON转Markdown ====================
    @staticmethod
    def json_to_markdown(json_data):
        """
        将文档解析返回的JSON转换为可读的Markdown格式。
        提取所有文本，按顺序拼接，并尝试识别表格。
        """
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except:
                return json_data  # 不是有效JSON，直接返回
        
        # 递归提取所有文本
        texts = []
        
        def extract_text(obj, path=""):
            if isinstance(obj, dict):
                # 如果有text字段，提取
                if 'text' in obj and isinstance(obj['text'], str):
                    texts.append(obj['text'].strip())
                # 如果有elements或result数组，遍历
                for key, value in obj.items():
                    if key in ['elements', 'result', 'data', 'results', 'output']:
                        extract_text(value, path + "." + key)
                    elif key == 'text' and isinstance(value, list):
                        # 如果是text数组
                        for item in value:
                            if isinstance(item, dict) and 'text' in item:
                                texts.append(item['text'].strip())
                            elif isinstance(item, str):
                                texts.append(item.strip())
                    else:
                        # 其他字段递归
                        extract_text(value, path + "." + key)
            elif isinstance(obj, list):
                for item in obj:
                    extract_text(item, path)
        
        extract_text(json_data)
        
        # 过滤空字符串
        texts = [t for t in texts if t]
        
        if not texts:
            return "（未提取到任何文本内容）"
        
        # 尝试组织成Markdown：简单拼接，连续文本合并为段落
        # 如果文本中有换行，可能表示不同段落
        # 这里简单处理，每个文本块作为一行
        # 可以进一步检测表格结构（如包含|的文本）
        md_lines = []
        for t in texts:
            # 如果文本包含制表符或多个空格，可能为表格
            if '\t' in t or '  ' in t:
                # 尝试转换为表格
                rows = t.strip().split('\n')
                if len(rows) > 1:
                    # 简单表格
                    table_rows = []
                    for row in rows:
                        cells = row.split('\t')
                        if len(cells) < 2:
                            cells = row.split('  ')  # 双空格分隔
                        if len(cells) >= 2:
                            table_rows.append('| ' + ' | '.join(cells) + ' |')
                    if table_rows:
                        # 添加表头分隔线
                        if len(table_rows) >= 2:
                            # 假设第一行为表头
                            header = table_rows[0]
                            # 生成分隔线
                            sep = '|' + '|'.join([' --- '] * (header.count('|')-1)) + '|'
                            md_lines.append(header)
                            md_lines.append(sep)
                            for row in table_rows[1:]:
                                md_lines.append(row)
                        else:
                            md_lines.extend(table_rows)
                        continue
            # 否则作为普通段落
            md_lines.append(t)
        
        return '\n\n'.join(md_lines)  # 用空行分隔段落
    
    # ==================== 任务处理 ====================
    def process_task(self, file_path, output_dir):
        try:
            func = self.function_var.get()
            if func == "ocr":
                result = self.ocr_recognize(file_path)
                self.root.after(0, self.update_result, result)
            elif func == "parse":
                raw = self.parse_document(file_path)
                # 下载文件
                task_id = raw.get('task_id', 'unknown')
                urls = raw.get('download_urls', [])
                if not urls:
                    self.root.after(0, self.update_result, f"⚠️ 文档解析完成，但未返回下载链接。任务ID: {task_id}")
                else:
                    local_paths, content = self.download_files(urls, task_id, output_dir)
                    # 如果有JSON文件，尝试转换为Markdown
                    markdown_content = ""
                    for path in local_paths:
                        if path.endswith('.json') and os.path.exists(path):
                            try:
                                with open(path, 'r', encoding='utf-8') as f:
                                    json_data = json.load(f)
                                    markdown_content = self.json_to_markdown(json_data)
                                    break
                            except Exception as e:
                                markdown_content = f"（解析JSON为Markdown时出错: {e}）"
                    # 构建结果信息
                    result_lines = [f"✅ 文档解析完成", f"任务ID: {task_id}"]
                    result_lines.append("文件已保存至:")
                    for p in local_paths:
                        result_lines.append(f"  {p}")
                    if markdown_content:
                        result_lines.append("\n📝 整理后的内容（Markdown格式）：")
                        result_lines.append("```markdown")
                        result_lines.append(markdown_content)
                        result_lines.append("```")
                    elif content:
                        result_lines.append("\n文件内容预览（非JSON）：")
                        result_lines.append(content)
                    else:
                        result_lines.append("\n（未提取到可展示的内容）")
                    self.root.after(0, self.update_result, "\n".join(result_lines))
            else:  # convert
                raw = self.convert_document(file_path, self.convert_format.get())
                task_id = raw.get('task_id', 'unknown')
                urls = raw.get('download_urls', [])
                if not urls:
                    self.root.after(0, self.update_result, f"⚠️ 格式转换完成，但未返回下载链接。任务ID: {task_id}")
                else:
                    local_paths, content = self.download_files(urls, task_id, output_dir)
                    result_lines = [
                        f"✅ 格式转换完成 (目标: {self.convert_format.get()})",
                        f"任务ID: {task_id}",
                        "文件已保存至:"
                    ]
                    for p in local_paths:
                        result_lines.append(f"  {p}")
                    if content:
                        result_lines.append("\n文件内容预览:")
                        result_lines.append(content)
                    self.root.after(0, self.update_result, "\n".join(result_lines))
        except Exception as e:
            error_msg = f"❌ 处理失败: {str(e)}"
            self.root.after(0, self.update_result, error_msg)
        finally:
            self.root.after(0, self.task_complete)
    
    # ==================== 通用OCR ====================
    def ocr_recognize(self, file_path, retries=3):
        url = f"{self.api_base}/ocr/recognize"
        display_name = self.ocr_type.get().strip()
        ocr_type = OCR_DISPLAY_TO_CODE.get(display_name, "GENERAL")
        payload = {'ocrType': ocr_type}
        file_name = os.path.basename(file_path)
        mime_type = self.get_mime_type(file_path)
        
        for attempt in range(retries):
            try:
                with open(file_path, 'rb') as f:
                    files = [('file', (file_name, f, mime_type))]
                    headers = self.get_headers()
                    response = requests.post(url, headers=headers, data=payload,
                                            files=files, timeout=(10, 60))
                if response.status_code != 200:
                    raise Exception(f"OCR识别失败: HTTP {response.status_code}, {response.text}")
                data = response.json()
                texts = []
                for item in data.get('data', []):
                    for res in item.get('result', []):
                        elem = res.get('elements', {})
                        for text_obj in elem.get('text', []):
                            text = text_obj.get('text', '').strip()
                            if text:
                                texts.append(text)
                if texts:
                    return "\n".join(texts)
                else:
                    return "⚠️ 未识别到任何文字"
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    ConnectionResetError) as e:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                else:
                    raise Exception(f"网络请求失败（已重试{retries}次）: {str(e)}")
            except Exception as e:
                raise Exception(f"OCR识别错误: {str(e)}")
    
    # ==================== 文档解析 ====================
    def parse_document(self, file_path, retries=3):
        submit_url = f"{self.api_base}/ocrdoc/submit"
        file_name = os.path.basename(file_path)
        mime_type = self.get_mime_type(file_path)
        
        data_params = {'ocr_type': 'DOC_PARING'}
        if self.is_table_cls.get():
            data_params['is_table_cls'] = 'true'
        if self.is_doc_ori.get():
            data_params['is_doc_ori'] = 'true'
        if self.enforce_seal.get():
            data_params['enforce_seal'] = 'true'
        if self.is_inline_formula.get():
            data_params['is_inline_formula'] = 'true'
        
        # 提交任务
        for attempt in range(retries):
            try:
                with open(file_path, 'rb') as f:
                    files = [('file', (file_name, f, mime_type))]
                    headers = self.get_headers()
                    response = requests.post(submit_url, headers=headers,
                                            data=data_params, files=files,
                                            timeout=(10, 120))
                if response.status_code != 200:
                    raise Exception(f"提交文档解析任务失败: HTTP {response.status_code}, {response.text}")
                result = response.json()
                if result.get('code') != '0':
                    raise Exception(f"提交失败: {result.get('msg', '未知错误')}")
                data = result.get('data', {})
                output = data.get('output', {})
                task_id = output.get('task_id')
                if not task_id:
                    raise Exception("未获取到任务ID")
                break
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    ConnectionResetError) as e:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                else:
                    raise Exception(f"提交任务失败（已重试{retries}次）: {str(e)}")
        
        # 轮询结果
        result_url = f"{self.api_base}/ocrdoc/result"
        max_attempts = 60
        attempt = 0
        while attempt < max_attempts:
            time.sleep(2)
            try:
                headers = self.get_headers()
                payload = {'task_ids': [task_id]}
                response = requests.post(result_url, headers=headers,
                                        json=payload, timeout=(10, 30))
                if response.status_code != 200:
                    attempt += 1
                    continue
                result_data = response.json()
                if result_data.get('code') != '0':
                    attempt += 1
                    continue
                data_list = result_data.get('data', [])
                if not data_list:
                    attempt += 1
                    continue
                task_result = data_list[0]
                output = task_result.get('output', {})
                task_status = output.get('task_status', '')
                if task_status == 'succeeded':
                    results = output.get('results', [])
                    return {
                        'status': 'success',
                        'task_id': task_id,
                        'download_urls': results
                    }
                elif task_status in ['failed', 'unknown']:
                    error_msg = output.get('error_message', '未知错误')
                    raise Exception(f"文档解析失败: {error_msg}")
                attempt += 1
            except requests.exceptions.RequestException as e:
                attempt += 1
                if attempt >= max_attempts:
                    raise Exception(f"轮询结果时网络错误: {str(e)}")
                continue
        raise Exception(f"文档解析超时（已等待{max_attempts * 2}秒）")
    
    # ==================== 格式转换 ====================
    def convert_document(self, file_path, target_format, retries=3):
        submit_url = f"{self.api_base}/doc/convert/task"
        file_name = os.path.basename(file_path)
        mime_type = self.get_mime_type(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        
        # 选择ocr_type
        if target_format == 'docx':
            if ext in ['.pdf']:
                ocr_type = 'PDF_TO_WORD'
            elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp']:
                ocr_type = 'IMAGE_TO_WORD'
            else:
                ocr_type = 'PDF_TO_WORD'
        else:  # pptx
            if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp']:
                ocr_type = 'IMAGE_TO_PPT'
            else:
                raise Exception(f"目标格式 {target_format} 不支持当前文件类型，图片可转PPT")
        
        data_params = {'ocr_type': ocr_type}
        if self.is_table_cls.get():
            data_params['is_table_cls'] = 'true'
        if self.is_doc_ori.get():
            data_params['is_doc_ori'] = 'true'
        if self.enforce_seal.get():
            data_params['enforce_seal'] = 'true'
        if self.is_inline_formula.get():
            data_params['is_inline_formula'] = 'true'
        
        # 提交
        for attempt in range(retries):
            try:
                with open(file_path, 'rb') as f:
                    files = [('file', (file_name, f, mime_type))]
                    headers = self.get_headers()
                    response = requests.post(submit_url, headers=headers,
                                            data=data_params, files=files,
                                            timeout=(10, 120))
                if response.status_code != 200:
                    raise Exception(f"提交转换任务失败: HTTP {response.status_code}, {response.text}")
                result = response.json()
                if result.get('code') != '0':
                    raise Exception(f"提交失败: {result.get('msg', '未知错误')}")
                data = result.get('data', {})
                output = data.get('output', {})
                task_id = output.get('task_id')
                if not task_id:
                    raise Exception("未获取到任务ID")
                break
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    ConnectionResetError) as e:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                else:
                    raise Exception(f"提交任务失败（已重试{retries}次）: {str(e)}")
        
        # 轮询
        result_url = f"{self.api_base}/ocrdoc/result"
        max_attempts = 60
        attempt = 0
        while attempt < max_attempts:
            time.sleep(2)
            try:
                headers = self.get_headers()
                payload = {'task_ids': [task_id]}
                response = requests.post(result_url, headers=headers,
                                        json=payload, timeout=(10, 30))
                if response.status_code != 200:
                    attempt += 1
                    continue
                result_data = response.json()
                if result_data.get('code') != '0':
                    attempt += 1
                    continue
                data_list = result_data.get('data', [])
                if not data_list:
                    attempt += 1
                    continue
                task_result = data_list[0]
                output = task_result.get('output', {})
                task_status = output.get('task_status', '')
                if task_status == 'succeeded':
                    results = output.get('results', [])
                    return {
                        'status': 'success',
                        'task_id': task_id,
                        'download_urls': results
                    }
                elif task_status in ['failed', 'unknown']:
                    error_msg = output.get('error_message', '未知错误')
                    raise Exception(f"格式转换失败: {error_msg}")
                attempt += 1
            except requests.exceptions.RequestException as e:
                attempt += 1
                if attempt >= max_attempts:
                    raise Exception(f"轮询结果时网络错误: {str(e)}")
                continue
        raise Exception(f"格式转换超时（已等待{max_attempts * 2}秒）")
    
    # ==================== 结果展示 ====================
    def update_result(self, result):
        self.result_text.delete(1.0, tk.END)
        if isinstance(result, str):
            try:
                self.result_text.insert(1.0, result)
            except:
                self.result_text.insert(1.0, result.encode('utf-8', errors='ignore').decode('utf-8'))
        else:
            try:
                formatted = json.dumps(result, indent=2, ensure_ascii=False)
                self.result_text.insert(1.0, formatted)
            except:
                self.result_text.insert(1.0, str(result))
    
    def clear_result(self):
        self.result_text.delete(1.0, tk.END)
    
    def task_complete(self):
        self.progress.stop()
        self.execute_btn.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()