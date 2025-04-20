use ab_glyph::{FontArc, PxScale};
use image::ImageReader;
use image::{DynamicImage, Rgba, RgbaImage};
use imageproc::drawing::draw_text_mut;
use std::fs;

fn read_image(path: &str) -> DynamicImage {
    ImageReader::open(path).unwrap().decode().unwrap()
}

fn to_grayscale(img: DynamicImage) -> DynamicImage {
    img.grayscale()
}

fn resize(img: DynamicImage, width: u32, height: u32) -> DynamicImage {
    img.resize_exact(width, height, image::imageops::FilterType::Lanczos3)
}

fn add_watermark(img: &DynamicImage, text: &str, font_path: &str) -> RgbaImage {
    let mut img = img.to_rgba8();
    let font_data = fs::read(font_path).expect("Font file not found");
    let font = FontArc::try_from_vec(font_data).expect("Invalid font format");
    let scale = PxScale::from(20.0);

    draw_text_mut(&mut img, Rgba([255, 0, 0, 255]), 10, 10, scale, &font, text);
    img
}

fn save_image(img: &RgbaImage, output_path: &str) {
    let rgb_image = image::DynamicImage::ImageRgba8(img.clone()).into_rgb8();
    rgb_image.save(output_path).unwrap();
}

fn main() {
    let input_path = "input/input.jpg";
    let output_path = "output.jpg";
    let font_path = "assets/TitilliumWeb-Regular.ttf"; // <-- use your font here

    let img = read_image(input_path);
    let img = to_grayscale(img);
    let img = resize(img, 300, 300);
    let img = add_watermark(&img, "Pipe-and-Filter", font_path);
    save_image(&img, output_path);

    println!("Gambar berhasil diproses dan disimpan ke {}", output_path);
}
