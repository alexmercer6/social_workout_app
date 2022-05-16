editBtns = document.querySelectorAll('.edit-btn')
weightForm = document.querySelector('.weight-form')
heightForm = document.querySelector('.height-form')

editBtns[0].addEventListener('click', function() {
    heightForm.classList.toggle('show-form')
    console.log('click')
})

editBtns[1].addEventListener('click', function() {
    weightForm.classList.toggle('show-form')
    console.log('click')
})
