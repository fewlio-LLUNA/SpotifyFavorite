document.addEventListener("DOMContentLoaded", () => {
    const carouselTrack = document.querySelector(".carousel-track");

    // Flask の static ディレクトリ内の画像を参照
    const images = [
        "./static/images/backnumber.jpg",
        "./static/images/idol.jpg",
        "./static/images/misutiru.jpg",
        "./static/images/snowman.jpg",
        "./static/images/twice.jpg",
        "./static/images/yusya.jpg",
    ];

    // 画像をランダムに並び替え
    const shuffledImages = images.sort(() => Math.random() - 0.5);

    // スライダーに画像を追加
    shuffledImages.forEach(imgUrl => {
        const imgElement = document.createElement("img");
        imgElement.src = imgUrl;
        carouselTrack.appendChild(imgElement);
    });
});
