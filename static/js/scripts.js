// Placeholder for any future JS, e.g. form validation or enhancements
document.addEventListener('DOMContentLoaded', () => {
  console.log('Page loaded and ready.');
  // Example: enable predict stage button only if all fields filled (could be expanded)
   const inputs = document.querySelectorAll('.form-control');
  inputs.forEach(input => {
    function toggleLabel() {
      if (input.value.trim() !== '') {
        input.classList.add('filled');
      } else {
        input.classList.remove('filled');
      }
    }
    input.addEventListener('input', toggleLabel);
    toggleLabel(); // initial call in case of prefilled values
  });
});




