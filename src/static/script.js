document.addEventListener("DOMContentLoaded", () => {
    const carouselTrack = document.querySelector(".carousel-track");

    const images = [
        "./static/images/backnumber.jpg",
        "./static/images/idol.jpg",
        "./static/images/misutiru.jpg",
        "./static/images/snowman.jpg",
        "./static/images/twice.jpg",
        "./static/images/yusya.jpg",
        "./static/images/1d.jpg",
        "./static/images/GRAY.jpg",
        "./static/images/miwa.jpg",
        "./static/images/keyaki.jpg",
    ];

    // 画像リストを50回繰り返す
    const repeatedImages = [];
    for (let i = 0; i < 50; i++) {
        repeatedImages.push(...images);
    }

    // 画像をスライダーに追加
    repeatedImages.forEach(imgUrl => {
        const imgElement = document.createElement("img");
        imgElement.src = imgUrl;
        carouselTrack.appendChild(imgElement);
    });

    let scrollAmount = 0;
    const slideSpeed = 0.5; // 1フレームあたりの移動距離（px）
    
    function moveCarousel() {
        scrollAmount += slideSpeed;
        carouselTrack.style.transform = `translateX(-${scrollAmount}px)`;

        // 一定量スクロールしたら、最初の方に戻す
        const firstImageWidth = carouselTrack.firstElementChild.clientWidth;
        const totalScrollWidth = firstImageWidth * repeatedImages.length;
        
        if (scrollAmount >= totalScrollWidth / 2) {
            scrollAmount = 0;
            carouselTrack.style.transform = `translateX(0)`;
        }

        requestAnimationFrame(moveCarousel);
    }

    moveCarousel(); // アニメーション開始
});
