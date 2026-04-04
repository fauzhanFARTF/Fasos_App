// ✅ Menggunakan Vanilla JavaScript (Lebih aman & modern)
document.addEventListener('DOMContentLoaded', function () {
  var tipeSelect = document.getElementById('id_tipe');
  if (!tipeSelect) return;

  var jenisInput = document.getElementById('id_jenis');
  var tingkatanInput = document.getElementById('id_tingkatan');

  if (!jenisInput || !tingkatanInput) return;

  var jenisRow = jenisInput.closest('.form-row');
  var tingkatanRow = tingkatanInput.closest('.form-row');

  function toggleFields() {
    var selectedValue = tipeSelect.value;

    if (selectedValue === 'Rumah Sakit') {
      // Tampilkan field Jenis & Tingkatan
      if (jenisRow) jenisRow.style.display = '';
      if (tingkatanRow) tingkatanRow.style.display = '';
    } else {
      // Sembunyikan field & set nilai ke "-"
      if (jenisRow) jenisRow.style.display = 'none';
      if (tingkatanRow) tingkatanRow.style.display = 'none';

      jenisInput.value = '-';
      tingkatanInput.value = '-';
    }
  }

  // Jalankan saat halaman dimuat (untuk mode Edit)
  toggleFields();

  // Jalankan saat user mengganti pilihan Tipe
  tipeSelect.addEventListener('change', toggleFields);
});
