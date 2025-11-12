<script>
  (function () {
    const input = document.getElementById('{{ form.auto_file.id_for_label }}');
    const zone  = document.getElementById('dropZone');
    const info  = document.getElementById('chosenFile');

    if (zone && input) {
      zone.addEventListener('click', () => input.click());

      zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('bg-blue-50');
      });
      zone.addEventListener('dragleave', () => {
        zone.classList.remove('bg-blue-50');
      });
      zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('bg-blue-50');
        if (e.dataTransfer.files && e.dataTransfer.files.length) {
          input.files = e.dataTransfer.files;
          info.textContent = e.dataTransfer.files[0].name;
          info.classList.remove('hidden');
        }
      });

      input.addEventListener('change', (e) => {
        const f = e.target.files && e.target.files[0];
        if (f) {
          info.textContent = f.name;
          info.classList.remove('hidden');
        }
      });
    }
  })();
</script>