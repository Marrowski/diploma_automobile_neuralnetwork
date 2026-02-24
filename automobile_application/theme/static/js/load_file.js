<script>
(function(){
  const imgDrop = document.getElementById('dropImg');
  const imgInput = document.getElementById('{{ form.image.id_for_label }}');
  const imgInfo = document.getElementById('imgInfo');

  const vidDrop = document.getElementById('dropVid');
  const vidInput = document.getElementById('{{ form.video.id_for_label }}');
  const vidInfo = document.getElementById('vidInfo');

  function attach(zone, input, info){
    if(!zone || !input) return;
    zone.addEventListener('click', ()=> input.click());
    zone.addEventListener('dragover', (e)=>{ e.preventDefault(); zone.classList.add('bg-blue-50'); });
    zone.addEventListener('dragleave', ()=> zone.classList.remove('bg-blue-50'));
    zone.addEventListener('drop', (e)=>{
      e.preventDefault(); zone.classList.remove('bg-blue-50');
      if(e.dataTransfer.files && e.dataTransfer.files.length){
        input.files = e.dataTransfer.files;
        if(info){ info.textContent = e.dataTransfer.files[0].name; info.classList.remove('hidden'); }
      }
    });
    input.addEventListener('change', (e)=>{
      const f = e.target.files && e.target.files[0];
      if(f && info){ info.textContent = f.name; info.classList.remove('hidden'); }
      // взаємовиключення: якщо обрав фото — чистимо відео, і навпаки
      if(input === imgInput && vidInput){ vidInput.value = ""; if(vidInfo) vidInfo.classList.add('hidden'); }
      if(input === vidInput && imgInput){ imgInput.value = ""; if(imgInfo) imgInfo.classList.add('hidden'); }
    });
  }
  attach(imgDrop, imgInput, imgInfo);
  attach(vidDrop, vidInput, vidInfo);
})();
</script>