import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import random
import os
import threading
import struct

class ElGamalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Криптосистема Эль-Гамаля")
        self.root.geometry("1100x800")
        
        self.primitive_roots = []
        self.p = None
        self.g = None
        self.x = None
        self.y = None
        
        self.setup_ui()
    
    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.key_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.key_frame, text="1. Генерация ключей")
        self.setup_key_tab()
        
        self.encrypt_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.encrypt_frame, text="2. Шифрование")
        self.setup_encrypt_tab()
        
        self.decrypt_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.decrypt_frame, text="3. Дешифрование")
        self.setup_decrypt_tab()
        
        self.view_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.view_frame, text="4. Просмотр файлов")
        self.setup_view_tab()
    
    def setup_key_tab(self):
        frame_p = ttk.LabelFrame(self.key_frame, text="Параметр p (простое число)")
        frame_p.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_p, text="Введите простое число p:").pack(side='left', padx=5)
        self.p_entry = ttk.Entry(frame_p, width=20)
        self.p_entry.pack(side='left', padx=5)
        self.p_entry.bind('<KeyRelease>', self.update_key_info)  # проверка при вводе
        
        ttk.Button(frame_p, text="Найти все первообразные корни", 
                   command=self.find_all_primitive_roots_thread).pack(side='left', padx=5)
        
        frame_g = ttk.LabelFrame(self.key_frame, text="Выбор первообразного корня g")
        frame_g.pack(fill='x', padx=10, pady=5)
        
        self.g_var = tk.StringVar()
        self.g_combo = ttk.Combobox(frame_g, textvariable=self.g_var, state='readonly', width=30)
        self.g_combo.pack(side='left', padx=5)
        self.g_combo.bind('<<ComboboxSelected>>', self.update_key_info)
        
        ttk.Label(frame_g, text="Количество корней:").pack(side='left', padx=5)
        self.roots_count_label = ttk.Label(frame_g, text="0", foreground="blue")
        self.roots_count_label.pack(side='left', padx=5)
        
        frame_x = ttk.LabelFrame(self.key_frame, text="Закрытый ключ x")
        frame_x.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_x, text="Введите x (1 < x < p-1):").pack(side='left', padx=5)
        self.x_entry = ttk.Entry(frame_x, width=20)
        self.x_entry.pack(side='left', padx=5)
        self.x_entry.bind('<KeyRelease>', self.update_key_info)
        
        # Информация о проверках ключей
        self.key_info_label = ttk.Label(self.key_frame, text="", foreground="blue")
        self.key_info_label.pack(pady=5)
        
        ttk.Button(self.key_frame, text="Вычислить открытый ключ y = g^x mod p", 
                   command=self.generate_keys).pack(pady=10)
        
        self.keys_text = scrolledtext.ScrolledText(self.key_frame, height=12, width=90)
        self.keys_text.pack(padx=10, pady=10, fill='both', expand=True)
        
        self.status_label = ttk.Label(self.key_frame, text="Готов", foreground="green")
        self.status_label.pack(pady=5)
    
    def setup_encrypt_tab(self):
        ttk.Label(self.encrypt_frame, text="Выберите файл для шифрования:").pack(pady=5)
        frame_file = ttk.Frame(self.encrypt_frame)
        frame_file.pack(fill='x', padx=10)
        
        self.encrypt_file_label = ttk.Label(frame_file, text="Файл не выбран", foreground="gray")
        self.encrypt_file_label.pack(side='left', padx=5)
        ttk.Button(frame_file, text="Выбрать файл", 
                   command=lambda: self.select_file("encrypt")).pack(side='right', padx=5)
        
        frame_k = ttk.LabelFrame(self.encrypt_frame, text="Параметр k (взаимно простой с p-1, 1 < k < p-1)")
        frame_k.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_k, text="Введите k для первого блока:").pack(side='left', padx=5)
        self.k_entry = ttk.Entry(frame_k, width=20)
        self.k_entry.pack(side='left', padx=5)
        self.k_entry.bind('<KeyRelease>', self.update_encrypt_info)  # проверка при вводе
        
        # Информация о проверках
        info_frame = ttk.LabelFrame(self.encrypt_frame, text="Информация о проверках")
        info_frame.pack(fill='x', padx=10, pady=5)
        self.info_label = tk.Label(info_frame, text="", foreground="blue", justify="left", font=("Arial", 10))
        self.info_label.pack(padx=5, pady=5, anchor="w")
        
        ttk.Button(self.encrypt_frame, text="Зашифровать файл", 
                   command=self.encrypt_file_thread).pack(pady=10)
        
        self.encrypt_result = scrolledtext.ScrolledText(self.encrypt_frame, height=15, width=90)
        self.encrypt_result.pack(padx=10, pady=10, fill='both', expand=True)
    
    def setup_decrypt_tab(self):
        ttk.Label(self.decrypt_frame, text="Выберите зашифрованный файл:").pack(pady=5)
        frame_file = ttk.Frame(self.decrypt_frame)
        frame_file.pack(fill='x', padx=10)
        
        self.decrypt_file_label = ttk.Label(frame_file, text="Файл не выбран", foreground="gray")
        self.decrypt_file_label.pack(side='left', padx=5)
        ttk.Button(frame_file, text="Выбрать файл", 
                   command=lambda: self.select_file("decrypt")).pack(side='right', padx=5)
        
        frame_keys = ttk.LabelFrame(self.decrypt_frame, text="Ключи для расшифровки")
        frame_keys.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_keys, text="Закрытый ключ x:").pack(side='left', padx=5)
        self.decrypt_x_entry = ttk.Entry(frame_keys, width=20)
        self.decrypt_x_entry.pack(side='left', padx=5)
        
        ttk.Label(frame_keys, text="Параметр p:").pack(side='left', padx=5)
        self.decrypt_p_entry = ttk.Entry(frame_keys, width=20)
        self.decrypt_p_entry.pack(side='left', padx=5)
        
        ttk.Button(self.decrypt_frame, text="Расшифровать файл", 
                   command=self.decrypt_file_thread).pack(pady=10)
        
        self.decrypt_result = scrolledtext.ScrolledText(self.decrypt_frame, height=15, width=90)
        self.decrypt_result.pack(padx=10, pady=10, fill='both', expand=True)
    
    def setup_view_tab(self):
        frame_view = ttk.Frame(self.view_frame)
        frame_view.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_view, text="Выберите файл:").pack(side='left', padx=5)
        self.view_file_label = ttk.Label(frame_view, text="Файл не выбран", foreground="gray")
        self.view_file_label.pack(side='left', padx=5)
        ttk.Button(frame_view, text="Выбрать файл", 
                   command=self.select_view_file).pack(side='right', padx=5)
        
        ttk.Button(self.view_frame, text="Показать содержимое", 
                   command=self.view_file_content).pack(pady=5)
        
        self.view_text = scrolledtext.ScrolledText(self.view_frame, height=25, width=90)
        self.view_text.pack(padx=10, pady=10, fill='both', expand=True)
    
    # ============= АЛГОРИТМЫ =============
    
    def fast_pow_mod(self, base, exp, mod):
        result = 1
        base = base % mod
        while exp > 0:
            if exp & 1:
                result = (result * base) % mod
            base = (base * base) % mod
            exp >>= 1
        return result
    
    def extended_gcd(self, a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = self.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    def mod_inverse(self, a, m):
        gcd, x, _ = self.extended_gcd(a, m)
        if gcd != 1:
            return None
        return x % m
    
    def is_coprime(self, a, b):
        gcd, _, _ = self.extended_gcd(a, b)
        return gcd == 1
    
    def get_prime_factors(self, n):
        factors = []
        i = 2
        temp = n
        while i * i <= temp:
            if temp % i == 0:
                factors.append(i)
                while temp % i == 0:
                    temp //= i
            i += 1
        if temp > 1:
            factors.append(temp)
        return factors
    
    def is_primitive_root(self, g, p, prime_factors):
        if g == 1:
            return False
        phi = p - 1
        for q in prime_factors:
            if self.fast_pow_mod(g, phi // q, p) == 1:
                return False
        return True
    
    def find_all_primitive_roots(self, p):
        if not self.is_prime(p):
            return []
        
        prime_factors = self.get_prime_factors(p - 1)
        roots = []
        for g in range(2, p):
            if self.is_primitive_root(g, p, prime_factors):
                roots.append(g)
        return roots
    
    def is_prime(self, n):
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    # ============= ПРОВЕРКИ В РЕАЛЬНОМ ВРЕМЕНИ =============
    
    def update_key_info(self, event=None):
        """Проверка вводимых ключей в реальном времени"""
        messages = []
        
        # Проверка p
        try:
            p = int(self.p_entry.get())
            if self.is_prime(p):
                messages.append(f"✓ p = {p} — простое число")
                if p > 255:
                    messages.append(f"  p > 255, можно шифровать любые файлы")
                else:
                    messages.append(f"  ⚠ p < 256, нельзя шифровать файлы с байтами > {p-1}")
            else:
                messages.append(f"✗ p = {p} — НЕ является простым числом")
        except ValueError:
            if self.p_entry.get():
                messages.append("✗ Введите целое число")
            else:
                messages.append("ⓘ Введите простое число p")
        
        # Проверка g (если есть корни)
        if self.primitive_roots and self.g_var.get():
            try:
                g = int(self.g_var.get())
                if g in self.primitive_roots:
                    messages.append(f"✓ g = {g} — первообразный корень по модулю p")
                else:
                    messages.append(f"✗ g = {g} — НЕ является первообразным корнем")
            except ValueError:
                pass
        
        # Проверка x
        try:
            p = int(self.p_entry.get()) if self.p_entry.get() else None
            x = int(self.x_entry.get()) if self.x_entry.get() else None
            
            if p and x:
                if 1 < x < p-1:
                    messages.append(f"✓ x = {x} в диапазоне (1, {p-1})")
                else:
                    messages.append(f"✗ x должно быть в диапазоне (1, {p-1})")
            elif x:
                messages.append("ⓘ Сначала введите p")
        except ValueError:
            if self.x_entry.get():
                messages.append("✗ Введите целое число для x")
        
        # Обновляем текст
        self.key_info_label.config(text="\n".join(messages))
        
        # Меняем цвет
        if any(msg.startswith("✗") for msg in messages):
            self.key_info_label.config(foreground="red")
        elif any(msg.startswith("✓") for msg in messages):
            self.key_info_label.config(foreground="green")
        else:
            self.key_info_label.config(foreground="blue")
    
    def update_encrypt_info(self, event=None):
        """Проверка вводимого k в реальном времени"""
        messages = []
        
        if self.p is None:
            messages.append("⚠ Сначала сгенерируйте ключи на вкладке 1")
            self.info_label.config(text="\n".join(messages), foreground="orange")
            return
        
        try:
            k = int(self.k_entry.get())
            
            # Проверка диапазона
            if 1 < k < self.p-1:
                messages.append(f"✓ k = {k} в диапазоне (1, {self.p-1})")
            else:
                messages.append(f"✗ k должно быть в диапазоне (1, {self.p-1})")
                messages.append(f"  Вы ввели k = {k}")
            
            # Проверка взаимной простоты
            if self.is_coprime(k, self.p-1):
                messages.append(f"✓ НОД({k}, {self.p-1}) = 1 (взаимно просты)")
            else:
                gcd_val = self.extended_gcd(k, self.p-1)[0]
                messages.append(f"✗ НОД({k}, {self.p-1}) = {gcd_val} (не взаимно просты!)")
                messages.append(f"  Для шифрования нужно взаимно простое число")
            
        except ValueError:
            if self.k_entry.get():
                messages.append("✗ Введите целое число")
            else:
                messages.append("ⓘ Введите k (2 до p-2)")
        
        # Обновляем текст
        self.info_label.config(text="\n".join(messages))
        
        # Меняем цвет
        if any(msg.startswith("✗") for msg in messages):
            self.info_label.config(foreground="red")
        elif any(msg.startswith("✓") for msg in messages):
            self.info_label.config(foreground="green")
        else:
            self.info_label.config(foreground="blue")
    
    # ============= ГЕНЕРАЦИЯ КЛЮЧЕЙ =============
    
    def find_all_primitive_roots_thread(self):
        def task():
            try:
                p = int(self.p_entry.get())
                
                if not self.is_prime(p):
                    messagebox.showerror("Ошибка проверки", 
                                        f"Число {p} не является простым!")
                    return
                
                if p < 3:
                    messagebox.showerror("Ошибка проверки", "p должно быть больше 2")
                    return
                
                self.status_label.config(text="Поиск первообразных корней...", foreground="orange")
                self.root.update()
                
                roots = self.find_all_primitive_roots(p)
                self.primitive_roots = roots
                self.p = p
                
                self.keys_text.delete(1.0, tk.END)
                self.keys_text.insert(tk.END, f"p = {p}\n")
                self.keys_text.insert(tk.END, f"p-1 = {p-1}\n")
                
                prime_factors = self.get_prime_factors(p-1)
                self.keys_text.insert(tk.END, f"Простые делители p-1: {prime_factors}\n\n")
                
                if roots:
                    self.keys_text.insert(tk.END, f"Найдено {len(roots)} первообразных корней:\n")
                    self.keys_text.insert(tk.END, f"{roots}\n\n")
                    
                    self.g_combo['values'] = [str(r) for r in roots]
                    self.roots_count_label.config(text=str(len(roots)))
                    self.status_label.config(text=f"Найдено {len(roots)} первообразных корней", foreground="green")
                    messagebox.showinfo("Успех", f"Найдено {len(roots)} первообразных корней")
                else:
                    self.status_label.config(text="Первообразные корни не найдены", foreground="red")
                    messagebox.showwarning("Предупреждение", "Первообразные корни не найдены")
                
                self.update_key_info()  # Обновляем проверки
                    
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное целое число")
        
        threading.Thread(target=task, daemon=True).start()
    
    def generate_keys(self):
        try:
            p = int(self.p_entry.get())
            g = int(self.g_var.get())
            x = int(self.x_entry.get())
            
            if not self.is_prime(p):
                messagebox.showerror("Ошибка", f"Число {p} не является простым!")
                return
            
            if g not in self.primitive_roots:
                messagebox.showerror("Ошибка", f"Число {g} не является первообразным корнем!")
                return
            
            if not (1 < x < p-1):
                messagebox.showerror("Ошибка", f"x должно быть в диапазоне (1, {p-1})")
                return
            
            self.p = p
            self.g = g
            self.x = x
            self.y = self.fast_pow_mod(g, x, p)
            
            self.keys_text.delete(1.0, tk.END)
            self.keys_text.insert(tk.END, "=== Генерация ключей (алгоритм Эль-Гамаля) ===\n\n")
            self.keys_text.insert(tk.END, f"1. Простое число p = {p}\n")
            self.keys_text.insert(tk.END, f"2. Первообразный корень g = {g}\n")
            self.keys_text.insert(tk.END, f"3. Закрытый ключ x = {x}\n")
            self.keys_text.insert(tk.END, f"4. Вычисляем y = g^x mod p:\n")
            self.keys_text.insert(tk.END, f"   y = {g}^{x} mod {p} = {self.y}\n\n")
            self.keys_text.insert(tk.END, f"Открытый ключ K_o = ({p}, {g}, {self.y})\n")
            self.keys_text.insert(tk.END, f"Закрытый ключ K_c = {x}\n")
            
            self.status_label.config(text="Ключи успешно сгенерированы", foreground="green")
            messagebox.showinfo("Успех", "Ключи успешно сгенерированы")
            
            self.update_encrypt_info()  # Обновляем проверки на вкладке шифрования
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
    
    # ============= ШИФРОВАНИЕ =============
    
    def select_file(self, mode):
        file_path = filedialog.askopenfilename(title="Выберите файл")
        if file_path:
            if mode == "encrypt":
                self.encrypt_file_label.config(text=os.path.basename(file_path), foreground="black")
                self.encrypt_file_path = file_path
            else:
                self.decrypt_file_label.config(text=os.path.basename(file_path), foreground="black")
                self.decrypt_file_path = file_path
    
    def select_view_file(self):
        file_path = filedialog.askopenfilename(title="Выберите файл для просмотра")
        if file_path:
            self.view_file_label.config(text=os.path.basename(file_path), foreground="black")
            self.view_file_path = file_path
    
    def view_file_content(self):
        try:
            file_path = getattr(self, 'view_file_path', None)
            if not file_path or not os.path.exists(file_path):
                messagebox.showerror("Ошибка", "Файл не выбран")
                return
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            self.view_text.delete(1.0, tk.END)
            self.view_text.insert(tk.END, f"Файл: {os.path.basename(file_path)}\n")
            self.view_text.insert(tk.END, f"Размер: {len(data)} байт\n\n")
            
            if file_path.endswith('.enc') and len(data) >= 8:
                original_len = struct.unpack('>I', data[0:4])[0]
                p = struct.unpack('>I', data[4:8])[0]
                
                self.view_text.insert(tk.END, "=" * 70 + "\n")
                self.view_text.insert(tk.END, "ЗАШИФРОВАННЫЙ ФАЙЛ\n")
                self.view_text.insert(tk.END, "=" * 70 + "\n")
                self.view_text.insert(tk.END, f"Исходный размер: {original_len} байт\n")
                self.view_text.insert(tk.END, f"Параметр p: {p}\n\n")
                
                self.view_text.insert(tk.END, "ПЕРВЫЕ 20 ПАР (a, b):\n")
                self.view_text.insert(tk.END, "-" * 50 + "\n")
                self.view_text.insert(tk.END, " №         a           b\n")
                self.view_text.insert(tk.END, "-" * 50 + "\n")
                
                pos = 8
                for i in range(20):
                    if pos + 8 <= len(data):
                        a = struct.unpack('>I', data[pos:pos+4])[0]
                        b = struct.unpack('>I', data[pos+4:pos+8])[0]
                        self.view_text.insert(tk.END, f"{i+1:3d}   {a:10d}   {b:10d}\n")
                        pos += 8
                    else:
                        break
                
                self.view_text.insert(tk.END, "-" * 50 + "\n")
                self.view_text.insert(tk.END, f"Всего пар: {(len(data) - 8) // 8}\n")
                
            else:
                self.view_text.insert(tk.END, "СОДЕРЖИМОЕ (числа 0-255):\n")
                self.view_text.insert(tk.END, "-" * 70 + "\n")
                numbers = list(data)
                for i, num in enumerate(numbers[:200]):
                    self.view_text.insert(tk.END, f"{num:3d} ")
                    if (i + 1) % 20 == 0:
                        self.view_text.insert(tk.END, "\n")
                self.view_text.insert(tk.END, f"\n... и ещё {len(numbers)-200 if len(numbers)>200 else 0} байт\n")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл: {str(e)}")
    
    def encrypt_file_thread(self):
        def task():
            try:
                if not hasattr(self, 'encrypt_file_path'):
                    messagebox.showerror("Ошибка", "Выберите файл для шифрования")
                    return
                
                if self.p is None or self.g is None or self.y is None:
                    messagebox.showerror("Ошибка", "Сначала сгенерируйте ключи на вкладке 1")
                    return
                
                try:
                    k_first = int(self.k_entry.get())
                except ValueError:
                    messagebox.showerror("Ошибка", "Введите корректное целое число для k")
                    return
                
                if not (1 < k_first < self.p-1):
                    messagebox.showerror("Ошибка", f"k должно быть в диапазоне (1, {self.p-1})")
                    return
                
                if not self.is_coprime(k_first, self.p-1):
                    messagebox.showerror("Ошибка", f"k = {k_first} и p-1 = {self.p-1} не взаимно просты!")
                    return
                
                with open(self.encrypt_file_path, 'rb') as f:
                    data = f.read()
                
                original_len = len(data)
                block_size = 8
                padding_len = (block_size - (original_len % block_size)) % block_size
                
                if padding_len > 0:
                    data += bytes([padding_len] * padding_len)
                
                max_byte = max(data) if data else 0
                if max_byte >= self.p:
                    messagebox.showerror("Ошибка", f"Байт {max_byte} >= p = {self.p}. Увеличьте p!")
                    return
                
                self.encrypt_result.delete(1.0, tk.END)
                self.encrypt_result.insert(tk.END, "=== Шифрование файла ===\n\n")
                self.encrypt_result.insert(tk.END, f"p = {self.p}, g = {self.g}, y = {self.y}\n")
                self.encrypt_result.insert(tk.END, f"k для первого блока = {k_first}\n")
                self.encrypt_result.insert(tk.END, f"Размер исходного файла: {original_len} байт\n")
                if padding_len > 0:
                    self.encrypt_result.insert(tk.END, f"Добавлен padding: {padding_len} байт(а)\n")
                self.encrypt_result.insert(tk.END, f"Размер с padding: {len(data)} байт\n\n")
                self.root.update()
                
                encrypted_pairs = []
                for i, byte_val in enumerate(data):
                    m = byte_val
                    
                    if i == 0:
                        k = k_first
                    else:
                        while True:
                            k = random.randint(2, self.p-2)
                            if self.is_coprime(k, self.p-1):
                                break
                    
                    a = self.fast_pow_mod(self.g, k, self.p)
                    yk = self.fast_pow_mod(self.y, k, self.p)
                    b = (yk * m) % self.p
                    encrypted_pairs.append((a, b))
                    
                    if (i + 1) % 100 == 0:
                        self.encrypt_result.insert(tk.END, f"Зашифровано {i+1} из {len(data)} байт...\n")
                        self.root.update()
                
                output_path = self.encrypt_file_path + ".enc"
                with open(output_path, 'wb') as f:
                    f.write(struct.pack('>I', original_len))
                    f.write(struct.pack('>I', self.p))
                    for a, b in encrypted_pairs:
                        f.write(struct.pack('>I', a))
                        f.write(struct.pack('>I', b))
                
                self.encrypt_result.insert(tk.END, f"\n=== Шифрование завершено ===\n")
                self.encrypt_result.insert(tk.END, f"Зашифрованный файл: {output_path}\n")
                self.encrypt_result.insert(tk.END, f"Всего пар (a,b): {len(encrypted_pairs)}\n\n")
                self.encrypt_result.insert(tk.END, "Первые 10 пар (a, b):\n")
                for i, (a, b) in enumerate(encrypted_pairs[:10]):
                    self.encrypt_result.insert(tk.END, f"{i+1}: a={a}, b={b}\n")
                
                messagebox.showinfo("Успех", f"Файл зашифрован: {output_path}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при шифровании: {str(e)}")
        
        threading.Thread(target=task, daemon=True).start()
    
    def decrypt_file_thread(self):
        def task():
            try:
                if not hasattr(self, 'decrypt_file_path'):
                    messagebox.showerror("Ошибка", "Выберите зашифрованный файл")
                    return
                
                try:
                    x = int(self.decrypt_x_entry.get())
                    p = int(self.decrypt_p_entry.get())
                except ValueError:
                    messagebox.showerror("Ошибка", "Введите корректные числовые значения")
                    return
                
                if not (1 < x < p-1):
                    messagebox.showerror("Ошибка", f"x должно быть в диапазоне (1, {p-1})")
                    return
                
                with open(self.decrypt_file_path, 'rb') as f:
                    data = f.read()
                
                if len(data) < 8:
                    messagebox.showerror("Ошибка", "Файл поврежден")
                    return
                
                original_len = struct.unpack('>I', data[:4])[0]
                saved_p = struct.unpack('>I', data[4:8])[0]
                
                if saved_p != p:
                    result = messagebox.askyesno("Предупреждение", 
                        f"p из файла ({saved_p}) не совпадает с введенным ({p})!\nИспользовать p из файла?")
                    if result:
                        p = saved_p
                    else:
                        return
                
                encrypted_pairs = []
                pos = 8
                while pos + 8 <= len(data):
                    a = struct.unpack('>I', data[pos:pos+4])[0]
                    b = struct.unpack('>I', data[pos+4:pos+8])[0]
                    encrypted_pairs.append((a, b))
                    pos += 8
                
                self.decrypt_result.delete(1.0, tk.END)
                self.decrypt_result.insert(tk.END, "=== Дешифрование файла ===\n\n")
                self.decrypt_result.insert(tk.END, f"p = {p}, x = {x}\n")
                self.decrypt_result.insert(tk.END, f"Исходный размер: {original_len} байт\n")
                self.decrypt_result.insert(tk.END, f"Количество пар: {len(encrypted_pairs)}\n\n")
                self.root.update()
                
                decrypted_data = bytearray()
                for i, (a, b) in enumerate(encrypted_pairs):
                    a_pow_x = self.fast_pow_mod(a, x, p)
                    a_pow_x_inv = self.mod_inverse(a_pow_x, p)
                    m = (b * a_pow_x_inv) % p
                    decrypted_data.append(m)
                    
                    if (i + 1) % 100 == 0:
                        self.decrypt_result.insert(tk.END, f"Расшифровано {i+1} из {len(encrypted_pairs)} байт...\n")
                        self.root.update()
                
                decrypted_bytes = bytes(decrypted_data)[:original_len]
                
                output_path = self.decrypt_file_path.replace(".enc", ".dec")
                with open(output_path, 'wb') as f:
                    f.write(decrypted_bytes)
                
                self.decrypt_result.insert(tk.END, f"\n=== Дешифрование завершено ===\n")
                self.decrypt_result.insert(tk.END, f"Расшифрованный файл: {output_path}\n")
                self.decrypt_result.insert(tk.END, f"Размер: {len(decrypted_bytes)} байт\n\n")
                
                messagebox.showinfo("Успех", f"Файл расшифрован: {output_path}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при дешифровании: {str(e)}")
        
        threading.Thread(target=task, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = ElGamalGUI(root)
    root.mainloop()
