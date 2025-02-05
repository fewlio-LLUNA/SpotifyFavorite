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

    // 画像をスライダーに追加
    images.forEach(imgUrl => {
        const imgElement = document.createElement("img");
        imgElement.src = imgUrl;
        carouselTrack.appendChild(imgElement);
    });

    // クローンを作成して無限ループを実現
    images.forEach(imgUrl => {
        const imgElement = document.createElement("img");
        imgElement.src = imgUrl;
        carouselTrack.appendChild(imgElement);
    });

    let scrollAmount = 0;
    const slideWidth = carouselTrack.firstElementChild.clientWidth;

    function moveCarousel() {
        scrollAmount += slideWidth;
        carouselTrack.style.transition = "transform 0.5s ease-in-out";
        carouselTrack.style.transform = `translateX(-${scrollAmount}px)`;

        // 画像が最後までスライドしたら、最初に戻す
        if (scrollAmount >= slideWidth * images.length) {
            setTimeout(() => {
                carouselTrack.style.transition = "none";  // 一時的にトランジションを無効にする
                scrollAmount = 0;
                carouselTrack.style.transform = "translateX(0)";  // 先頭に戻す

                // トランジションを再適用
                setTimeout(() => {
                    carouselTrack.style.transition = "transform 0.5s ease-in-out";
                }, 20);  // 20msの遅延を入れてからトランジションを再度適用
            }, 500);  // アニメーション終了後に0.5秒待つ
        }
    }

    setInterval(moveCarousel, 2000);
});
