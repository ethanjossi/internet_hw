const categorySelect = document.getElementById('newCategory');
const categoryLabel = document.getElementById('otherCategoryLabel');
const categoryInput = document.getElementById('otherCategoryText');

// Add the event listener to toggle showing the other category option
categorySelect.addEventListener('change', function() {
    if (categorySelect.value === 'other') {
        categoryLabel.hidden = false;
        categoryInput.hidden = false;
    } else {
        categoryLabel.hidden = true;
        categoryInput.hidden = true;
    }
});