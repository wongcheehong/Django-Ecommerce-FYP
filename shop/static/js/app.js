const config = {
    type: 'carousel',
    perView: 3,
    focusAt: 'center',
    autoplay: 1500,
    breakpoints: {
        800: {
            perView: 2
        },
        480: {
            perView: 1
        }
    }
}
new Glide('.glide', config).mount()
