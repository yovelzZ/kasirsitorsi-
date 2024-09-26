import streamlit as st
import json

# Struktur Data untuk BST dan List
class Node:
    def __init__(self, sku, nama, harga, stok):
        self.sku = sku
        self.nama = nama
        self.harga = harga
        self.stok = stok
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, sku, nama, harga, stok):
        if not self.root:
            self.root = Node(sku, nama, harga, stok)
        else:
            self._insert(self.root, sku, nama, harga, stok)

    def _insert(self, current, sku, nama, harga, stok):
        if sku < current.sku:
            if current.left:
                self._insert(current.left, sku, nama, harga, stok)
            else:
                current.left = Node(sku, nama, harga, stok)
        elif sku > current.sku:
            if current.right:
                self._insert(current.right, sku, nama, harga, stok)
            else:
                current.right = Node(sku, nama, harga, stok)
        else:
            st.warning("SKU sudah ada di BST.")

    def search(self, sku):
        return self._search(self.root, sku)

    def _search(self, current, sku):
        if not current:
            return None
        if sku == current.sku:
            return current
        elif sku < current.sku:
            return self._search(current.left, sku)
        else:
            return self._search(current.right, sku)

    def update_stok(self, sku, jumlah_baru):
        node = self.search(sku)
        if node:
            node.stok += jumlah_baru
            st.success(f"Stok untuk SKU {sku} diperbarui menjadi {node.stok}.")
        else:
            st.warning("SKU tidak ditemukan di BST.")

    def delete(self, sku):
        self.root = self._delete(self.root, sku)

    def _delete(self, current, sku):
        if not current:
            return None
        if sku < current.sku:
            current.left = self._delete(current.left, sku)
        elif sku > current.sku:
            current.right = self._delete(current.right, sku)
        else:
            if not current.left:
                return current.right
            if not current.right:
                return current.left
            temp = self._min_value_node(current.right)
            current.sku, current.nama, current.harga, current.stok = temp.sku, temp.nama, temp.harga, temp.stok
            current.right = self._delete(current.right, temp.sku)
        return current

    def _min_value_node(self, node):
        current = node
        while current.left:
            current = current.left
        return current

# Fungsi untuk Menyimpan Data ke File JSON
def save_data(bst, transactions, stok_file='stok.json', transaksi_file='transaksi.json'):
    def serialize_bst(node):
        if not node:
            return None
        return {
            'sku': node.sku,
            'nama': node.nama,
            'harga': node.harga,
            'stok': node.stok,
            'left': serialize_bst(node.left),
            'right': serialize_bst(node.right)
        }

    bst_data = serialize_bst(bst.root)
    with open(stok_file, 'w') as f:
        json.dump(bst_data, f)

    with open(transaksi_file, 'w') as f:
        json.dump(transactions, f)

# Fungsi untuk Memuat Data dari File JSON
def load_data(stok_file='stok.json', transaksi_file='transaksi.json'):
    def deserialize_bst(data):
        if not data:
            return None
        node = Node(data['sku'], data['nama'], data['harga'], data['stok'])
        node.left = deserialize_bst(data['left'])
        node.right = deserialize_bst(data['right'])
        return node

    bst = BST()
    try:
        with open(stok_file, 'r') as f:
            bst_data = json.load(f)
            bst.root = deserialize_bst(bst_data)
    except FileNotFoundError:
        bst = BST()

    try:
        with open(transaksi_file, 'r') as f:
            transactions = json.load(f)
    except FileNotFoundError:
        transactions = []

    return bst, transactions

# Fungsi Streamlit untuk Input dan Display
def main():
    # Load existing data
    bst, transactions = load_data()
    
    st.title("Program Pengelolaan Data Stok dan Transaksi Konsumen")

    menu = st.sidebar.selectbox("Menu Utama", ["Kelola Stok Barang", "Kelola Transaksi Konsumen", "Exit Program"])

    if menu == "Kelola Stok Barang":
        submenu = st.selectbox("Sub Menu", ["Input Data Stok Barang", "Restok Barang", "Lihat dan Edit Data Stok", "Kembali ke Menu Utama"])
        
        if submenu == "Input Data Stok Barang":
            with st.form("Input Data Stok Barang"):
                sku = st.text_input("No. SKU (4 digit angka)")
                nama = st.text_input("Nama Barang")
                harga = st.number_input("Harga Satuan", min_value=0)
                stok = st.number_input("Jumlah Stok", min_value=0)
                submitted = st.form_submit_button("Submit")
                
                if submitted:
                    if len(sku) == 4 and sku.isdigit():
                        if not bst.search(int(sku)):
                            bst.insert(int(sku), nama, harga, stok)
                            save_data(bst, transactions)  # Save data to file
                            st.success("Data stok barang berhasil ditambahkan.")
                        else:
                            st.warning("No. SKU sudah ada.")
                    else:
                        st.warning("No. SKU harus 4 digit angka.")

        elif submenu == "Restok Barang":
            with st.form("Restok Barang"):
                sku = st.text_input("No. SKU (4 digit angka)")
                jumlah_baru = st.number_input("Jumlah Stok Baru", min_value=0)
                submitted = st.form_submit_button("Submit")

                if submitted:
                    if len(sku) == 4 and sku.isdigit():
                        bst.update_stok(int(sku), jumlah_baru)
                        save_data(bst, transactions)  # Save data to file
                    else:
                        st.warning("No. SKU harus 4 digit angka.")
        
        elif submenu == "Lihat dan Edit Data Stok":
            # Display and Edit Stok Data
            def display_and_edit_stok(node):
                if node:
                    display_and_edit_stok(node.left)
                    col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 2, 2, 2, 2])
                    with col1:
                        st.write(node.sku)
                    with col2:
                        new_nama = st.text_input(f"Nama-{node.sku}", node.nama)
                    with col3:
                        new_harga = st.number_input(f"Harga-{node.sku}", value=node.harga, min_value=0)
                    with col4:
                        new_stok = st.number_input(f"Stok-{node.sku}", value=node.stok, min_value=0)
                    with col5:
                        if st.button(f"Update-{node.sku}"):
                            node.nama = new_nama
                            node.harga = new_harga
                            node.stok = new_stok
                            save_data(bst, transactions)
                            st.success(f"Data stok untuk SKU {node.sku} berhasil diperbarui.")
                    with col6:
                        if st.button(f"Hapus-{node.sku}"):
                            bst.delete(node.sku)
                            save_data(bst, transactions)
                            st.success(f"Data stok untuk SKU {node.sku} berhasil dihapus.")
                    display_and_edit_stok(node.right)

            st.write("Data Stok Barang")
            col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 2, 2, 2, 2])
            with col1:
                st.write("SKU")
            with col2:
                st.write("Nama Barang")
            with col3:
                st.write("Harga")
            with col4:
                st.write("Stok")
            with col5:
                st.write("Aksi")
            with col6:
                st.write("Hapus")
            display_and_edit_stok(bst.root)

    elif menu == "Kelola Transaksi Konsumen":
        submenu = st.selectbox("Sub Menu", ["Input Data Transaksi Baru", "Lihat Data Seluruh Transaksi Konsumen", "Lihat Data Transaksi Berdasarkan Subtotal", "Hapus Data Transaksi", "Kembali ke Menu Utama"])
        
        if submenu == "Input Data Transaksi Baru":
            with st.form("Input Data Transaksi Baru"):
                nama = st.text_input("Nama Konsumen")
                sku = st.text_input("No. SKU barang yang dibeli (4 digit angka)")
                jumlah_beli = st.number_input("Jumlah Beli", min_value=0)
                submitted = st.form_submit_button("Submit")
                
                if submitted:
                    if len(sku) == 4 and sku.isdigit():
                        barang = bst.search(int(sku))
                        if barang:
                            if barang.stok >= jumlah_beli:
                                subtotal = barang.harga * jumlah_beli
                                transactions.append((nama, sku, jumlah_beli, subtotal))
                                barang.stok -= jumlah_beli
                                save_data(bst, transactions)  # Save data to file
                                st.success("Data transaksi konsumen berhasil diinputkan.")
                            else:
                                st.warning("Jumlah stok tidak mencukupi.")
                        else:
                            st.warning("No. SKU tidak terdaftar.")
                    else:
                        st.warning("No. SKU harus 4 digit angka.")

        elif submenu == "Lihat Data Seluruh Transaksi Konsumen":
            st.write("Data Seluruh Transaksi Konsumen")
            for trans in transactions:
                st.write(f"Nama Konsumen: {trans[0]}, SKU: {trans[1]}, Jumlah Beli: {trans[2]}, Subtotal: {trans[3]}")

        elif submenu == "Lihat Data Transaksi Berdasarkan Subtotal":
            st.write("Data Transaksi Berdasarkan Subtotal")
            sorted_transactions = sorted(transactions, key=lambda x: x[3], reverse=True)
            for trans in sorted_transactions:
                st.write(f"Nama Konsumen: {trans[0]}, SKU: {trans[1]}, Jumlah Beli: {trans[2]}, Subtotal: {trans[3]}")

        elif submenu == "Hapus Data Transaksi":
            st.write("Hapus Data Transaksi")
            for i, trans in enumerate(transactions):
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
                with col1:
                    st.write(trans[0])
                with col2:
                    st.write(trans[1])
                with col3:
                    st.write(trans[2])
                with col4:
                    st.write(trans[3])
                with col5:
                    if st.button(f"Hapus-{i}"):
                        transactions.pop(i)
                        save_data(bst, transactions)
                        st.success("Data transaksi berhasil dihapus.")
                        break

if __name__ == "__main__":
    main()
