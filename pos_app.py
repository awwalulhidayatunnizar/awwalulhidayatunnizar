import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
import os
import tempfile

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class POSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Konfigurasi jendela utama
        self.title("Aplikasi Kasir - Velvet Mart")
        self.geometry("900x700")
        self.resizable(False, False)
        self.configure(bg_color="#e0e0e0")  # Background color untuk tampilan yang tidak polos

        # Kategori barang
        self.categories = {
            "Sembako (Beras, Telur, Terigu)": {"id_range": (1, 50), "price_range": (10000, 100000)},
            "Snack & Minuman (Chiki, Soda, Air Mineral)": {"id_range": (51, 150), "price_range": (2000, 15000)},
            "Bumbu Dapur (Garam, Kecap, Penyedap)": {"id_range": (151, 200), "price_range": (1500, 25000)},
            "Alat Tulis & Rumah Tangga (Buku, Sabun, Sapu)": {"id_range": (201, 300), "price_range": (5000, 150000)}
        }

        # Variabel untuk menyimpan data belanja
        self.items = []  # List of dicts: {'id': int, 'nama': str, 'harga': float, 'qty': int, 'subtotal': float}
        self.total = 0.0

        # Frame untuk input barang
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=10, padx=10, fill="x")

        # Label dan entry untuk nama barang
        self.nama_label = ctk.CTkLabel(self.input_frame, text="Nama Barang:")
        self.nama_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.nama_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Masukkan nama barang")
        self.nama_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Label dan entry untuk harga
        self.harga_label = ctk.CTkLabel(self.input_frame, text="Harga (Rp):")
        self.harga_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.harga_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Masukkan harga")
        self.harga_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Label dan entry untuk jumlah
        self.qty_label = ctk.CTkLabel(self.input_frame, text="Jumlah:")
        self.qty_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.qty_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Masukkan jumlah")
        self.qty_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Label dan combobox untuk kategori
        self.kategori_label = ctk.CTkLabel(self.input_frame, text="Kategori:")
        self.kategori_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.kategori_combobox = ctk.CTkComboBox(self.input_frame, values=list(self.categories.keys()), command=self.on_kategori_select)
        self.kategori_combobox.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Label dan entry untuk ID
        self.id_label = ctk.CTkLabel(self.input_frame, text="ID Barang:")
        self.id_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.id_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Masukkan ID barang")
        self.id_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # Tombol tambah barang
        self.tambah_button = ctk.CTkButton(self.input_frame, text="Tambah Barang", command=self.tambah_barang)
        self.tambah_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Frame untuk daftar belanja
        self.daftar_frame = ctk.CTkFrame(self)
        self.daftar_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.daftar_label = ctk.CTkLabel(self.daftar_frame, text="Daftar Belanja:")
        self.daftar_label.pack(pady=5)

        # Treeview untuk menampilkan daftar belanja
        self.tree = ctk.CTkScrollableFrame(self.daftar_frame)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Header untuk treeview
        self.header_frame = ctk.CTkFrame(self.tree)
        self.header_frame.pack(fill="x")
        ctk.CTkLabel(self.header_frame, text="ID", width=50).pack(side="left", padx=5)
        ctk.CTkLabel(self.header_frame, text="Nama", width=200).pack(side="left", padx=5)
        ctk.CTkLabel(self.header_frame, text="Harga", width=100).pack(side="left", padx=5)
        ctk.CTkLabel(self.header_frame, text="Qty", width=50).pack(side="left", padx=5)
        ctk.CTkLabel(self.header_frame, text="Subtotal", width=100).pack(side="left", padx=5)

        # Frame untuk total dan pembayaran
        self.total_frame = ctk.CTkFrame(self)
        self.total_frame.pack(pady=10, padx=10, fill="x")

        self.total_label = ctk.CTkLabel(self.total_frame, text="Total: Rp 0")
        self.total_label.pack(side="left", padx=10)

        # Label dan entry untuk uang bayar
        self.bayar_label = ctk.CTkLabel(self.total_frame, text="Uang Bayar (Rp):")
        self.bayar_label.pack(side="left", padx=10)
        self.bayar_entry = ctk.CTkEntry(self.total_frame, placeholder_text="Masukkan uang bayar")
        self.bayar_entry.pack(side="left", padx=10)

        # Tombol hitung kembalian
        self.hitung_button = ctk.CTkButton(self.total_frame, text="Hitung Kembalian", command=self.hitung_kembalian)
        self.hitung_button.pack(side="left", padx=10)

        # Label untuk kembalian
        self.kembalian_label = ctk.CTkLabel(self.total_frame, text="Kembalian: Rp 0")
        self.kembalian_label.pack(side="left", padx=10)

        # Frame untuk struk
        self.struk_frame = ctk.CTkFrame(self)
        self.struk_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.struk_label = ctk.CTkLabel(self.struk_frame, text="Struk Pembayaran:")
        self.struk_label.pack(pady=5)

        self.struk_text = ctk.CTkTextbox(self.struk_frame, wrap="word")
        self.struk_text.pack(fill="both", expand=True, padx=10, pady=5)

        # Tombol simpan struk dan print struk
        button_frame = ctk.CTkFrame(self.struk_frame)
        button_frame.pack(pady=5)
        self.simpan_button = ctk.CTkButton(button_frame, text="Simpan Struk", command=self.simpan_struk)
        self.simpan_button.pack(side="left", padx=5)
        self.print_button = ctk.CTkButton(button_frame, text="Klik Print", command=self.print_struk)
        self.print_button.pack(side="left", padx=5)

        # Tombol reset
        self.reset_button = ctk.CTkButton(self, text="Reset Transaksi", command=self.reset_transaksi)
        self.reset_button.pack(pady=10)

    def on_kategori_select(self, selected_kategori):
        # Set default price based on category
        price_range = self.categories[selected_kategori]["price_range"]
        default_price = price_range[0]  # Use min price as default
        self.harga_entry.delete(0, 'end')
        self.harga_entry.insert(0, str(default_price))

        # Set nama to category name
        self.nama_entry.delete(0, 'end')
        self.nama_entry.insert(0, selected_kategori.split(" (")[0])  # Take part before (

    def tambah_barang(self):
        # Ambil data dari entry
        nama = self.nama_entry.get().strip()
        harga_str = self.harga_entry.get().strip()
        qty_str = self.qty_entry.get().strip()
        id_str = self.id_entry.get().strip()

        # Validasi input
        if not nama or not harga_str or not qty_str or not id_str:
            messagebox.showerror("Error", "Semua field harus diisi!")
            return

        try:
            harga = float(harga_str)
            qty = int(qty_str)
            item_id = int(id_str)
            if harga <= 0 or qty <= 0 or item_id <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Harga, jumlah, dan ID harus angka positif!")
            return

        # Hitung subtotal
        subtotal = harga * qty

        # Tambah ke list items
        self.items.append({'id': item_id, 'nama': nama, 'harga': harga, 'qty': qty, 'subtotal': subtotal})

        # Update total
        self.total += subtotal
        self.total_label.configure(text=f"Total: Rp {self.total:,.0f}")

        # Tambah ke treeview
        item_frame = ctk.CTkFrame(self.tree)
        item_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(item_frame, text=str(item_id), width=50).pack(side="left", padx=5)
        ctk.CTkLabel(item_frame, text=nama, width=200).pack(side="left", padx=5)
        ctk.CTkLabel(item_frame, text=f"Rp {harga:,.0f}", width=100).pack(side="left", padx=5)
        ctk.CTkLabel(item_frame, text=str(qty), width=50).pack(side="left", padx=5)
        ctk.CTkLabel(item_frame, text=f"Rp {subtotal:,.0f}", width=100).pack(side="left", padx=5)

        # Clear entries
        self.nama_entry.delete(0, 'end')
        self.harga_entry.delete(0, 'end')
        self.qty_entry.delete(0, 'end')
        self.id_entry.delete(0, 'end')

        # Generate struk sementara
        self.generate_struk()

    def hitung_kembalian(self):
        bayar_str = self.bayar_entry.get().strip()
        if not bayar_str:
            messagebox.showerror("Error", "Masukkan uang bayar!")
            return

        try:
            bayar = float(bayar_str)
            if bayar < self.total:
                messagebox.showerror("Error", "Uang bayar kurang!")
                return
        except ValueError:
            messagebox.showerror("Error", "Uang bayar harus angka!")
            return

        kembalian = bayar - self.total
        self.kembalian_label.configure(text=f"Kembalian: Rp {kembalian:,.0f}")

        # Update struk dengan pembayaran
        self.generate_struk(bayar=bayar, kembalian=kembalian)

    def generate_struk(self, bayar=None, kembalian=None):
        # Header struk
        struk = "VELVET MART\n"
        struk += "=" * 30 + "\n"
        struk += f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        struk += "=" * 30 + "\n"

        # Daftar barang
        for item in self.items:
            struk += f"ID {item['id']}: {item['nama']} (x{item['qty']}) - Rp {item['harga']:,.0f} = Rp {item['subtotal']:,.0f}\n"

        struk += "=" * 30 + "\n"
        struk += f"Total: Rp {self.total:,.0f}\n"

        if bayar is not None:
            struk += f"Uang Bayar: Rp {bayar:,.0f}\n"
            struk += f"Kembalian: Rp {kembalian:,.0f}\n"

        struk += "\nTerima Kasih!\n"

        self.struk_text.delete("1.0", "end")
        self.struk_text.insert("1.0", struk)

    def simpan_struk(self):
        if not self.items:
            messagebox.showerror("Error", "Tidak ada transaksi untuk disimpan!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(self.struk_text.get("1.0", "end-1c"))
            messagebox.showinfo("Sukses", "Struk berhasil disimpan!")

    def print_struk(self):
        if not self.items:
            messagebox.showerror("Error", "Tidak ada transaksi untuk dicetak!")
            return

        struk_content = self.struk_text.get("1.0", "end-1c")
        if not struk_content.strip():
            messagebox.showerror("Error", "Struk kosong!")
            return

        try:
            # Buat file sementara
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(struk_content)
                temp_file_path = temp_file.name

            # Cetak menggunakan perintah sistem
            if os.name == 'nt':  # Windows
                os.startfile(temp_file_path, "print")
            else:  # Linux/Mac
                os.system(f"lpr {temp_file_path}")

            messagebox.showinfo("Sukses", "Struk sedang dicetak!")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal mencetak struk: {str(e)}")

    def reset_transaksi(self):
        # Reset semua data
        self.items = []
        self.total = 0.0
        self.total_label.configure(text="Total: Rp 0")
        self.kembalian_label.configure(text="Kembalian: Rp 0")
        self.bayar_entry.delete(0, 'end')

        # Clear treeview
        for widget in self.tree.winfo_children():
            if widget != self.header_frame:
                widget.destroy()

        # Clear struk
        self.struk_text.delete("1.0", "end")

if __name__ == "__main__":
    app = POSApp()
    app.mainloop()
