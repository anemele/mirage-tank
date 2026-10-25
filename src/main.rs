use image::GrayImage;

#[derive(Debug, argh:: FromArgs)]
/// make mirage tank image
struct Args {
    #[argh(positional)]
    /// top image
    top_img: String,

    #[argh(positional)]
    /// bottom image
    bottom_img: String,

    #[argh(option, short = 'o', default = r#""output.png".to_string()"#)]
    /// output image
    output: String,
}

fn main() {
    let args: Args = argh::from_env();

    let output = if args.output.ends_with(".png") {
        args.output
    } else {
        args.output + ".png"
    };

    if let Err(e) = make(&args.top_img, &args.bottom_img, &output) {
        eprintln!("error: {e}")
    }
}

fn same_size_and_center(img1: GrayImage, img2: GrayImage) -> (GrayImage, GrayImage) {
    let (w1, h1) = img1.dimensions();
    let (w2, h2) = img2.dimensions();
    let w = w1.max(w2);
    let h = h1.max(h2);

    let mut canv1 = GrayImage::new(w, h);
    let mut canv2 = GrayImage::new(w, h);
    image::imageops::overlay(&mut canv1, &img1, (w - w1) as i64 / 2, (h - h1) as i64 / 2);
    image::imageops::overlay(&mut canv2, &img2, (w - w2) as i64 / 2, (h - h2) as i64 / 2);

    (canv1, canv2)
}

fn make<P>(top_img: P, bottom_img: P, output_img: P) -> anyhow::Result<()>
where
    P: AsRef<std::path::Path>,
{
    let img1 = image::open(top_img)?.to_luma8();
    let img2 = image::open(bottom_img)?.to_luma8();
    let (img1, img2) = same_size_and_center(img1, img2);

    let top = img1.to_vec();
    let bottom = img2.to_vec();

    let mut ga = Vec::with_capacity(top.len() * 2);
    for (&t, &b) in top.iter().zip(bottom.iter()) {
        let t = t / 2 + 128;
        let b = b / 2;
        let a = if t == b { 0 } else { 255 - (t - b) };
        let g = if a == 0 {
            0
        } else {
            // let g = (b as f32) / (a as f32) * 255.;
            let g = 255 * b as u32 / a as u32;
            g as u8
        };
        ga.push(g);
        ga.push(a);
    }
    image::save_buffer(
        output_img,
        &ga,
        img1.width(),
        img1.height(),
        image::ColorType::La8,
    )?;

    Ok(())
}
