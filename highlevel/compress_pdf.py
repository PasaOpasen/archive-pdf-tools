import io
import os

import fitz
from PIL import Image
from hocr.parse import hocr_page_to_word_data

from internetarchivepdf.const import DENOISE_FAST, JPEG2000_IMPL_KAKADU, JPEG2000_IMPL_PILLOW, COMPRESSOR_JPEG
from internetarchivepdf.mrc import create_mrc_hocr_components, encode_mrc_images


def remove_images(doc, page, unwanted):
    un_list = [b"/%s Do" % u.encode() for u in unwanted]
    #page.clean_contents()  # unify / format the commands
    xref=page.get_contents()[0]  # get its XREF
    cont=page.read_contents().splitlines()  # read commands as list of lines
    for i in range(len(cont)):  # walk thru the lines
        if cont[i] in un_list:  # invokes an unwanted image
            cont[i] = b""  # remove command
    doc.update_stream(xref, b"\n".join(cont))  # replace cleaned command object
    #page.clean_contents()  # removes now unreferenced images from page definition


def compress_page_images(doc: fitz.Document, page: fitz.Page, hocr_word_data=[]):

    page.clean_contents()
    imgs = page.get_images(full=True)

    to_remove_xrefs = []
    to_insert = []

    for img_data in imgs:
        xref = img_data[0]
        #print(img_data)
        orig_img = doc.extract_image(xref)
        to_remove_xrefs.append(xref)
        bbox = page.get_image_bbox(img_data)
        #print(bbox)

        imgfd = io.BytesIO()
        imgfd.write(orig_img["image"])
        pil_image = Image.open(imgfd)
        pil_image.load()
        # TODO: if greyscale or 1bit, treat differently
        # TODO: force 1bit mode?
        #print('image mode', pil_image.mode)
        #print('image size', pil_image.size)

        imgfd.close()

        dpi = orig_img['xres']

        mrc_gen = create_mrc_hocr_components(
            pil_image,
            hocr_word_data,
            #mrc_gen = create_mrc_hocr_components(pil_image, [],
            denoise_mask=DENOISE_FAST,
            bg_downsample=3
        )

        encode_kwargs = dict(
            mrc_gen=mrc_gen,

            jbig2=True,
            embedded_jbig2=False,

            tmp_dir='./',
        )

        # with pillow
        encode_kwargs.update(
            dict(
                jpeg2000_implementation=JPEG2000_IMPL_PILLOW,
                bg_compression_flags=['quality_mode:"rates";quality_layers:[500]'],
                fg_compression_flags=['quality_mode:"rates";quality_layers:[750]'],
            )
        )

        # with jpegoptim
        # encode_kwargs.update(
        #     dict(
        #         mrc_image_format=COMPRESSOR_JPEG,
        #         bg_compression_flags=['-S30'],
        #         fg_compression_flags=['-S20'],
        #     )
        # )

        # fg_slope = 44500
        # bg_slope = 44250
        # encode_kwargs.update(
        #     dict(
        #         jpeg2000_implementation=JPEG2000_IMPL_KAKADU,
        #         bg_compression_flags=['-slope', str(bg_slope)],
        #         fg_compression_flags=['-slope', str(fg_slope)],
        #     )
        # )

        mask_f, bg_f, bg_s, fg_f, fg_s = encode_mrc_images(**encode_kwargs)

        # TODO: maybe we can replace the existing image with the background image
        # here
        bg_contents = open(bg_f, 'rb').read()
        fg_contents = open(fg_f, 'rb').read()
        mask_contents = open(mask_f, 'rb').read()

        os.remove(mask_f)
        os.remove(bg_f)
        os.remove(fg_f)

        to_insert.append([
            {'bbox': bbox, 'stream': bg_contents, 'mask': None, 'overlay': False},
            {'bbox': bbox, 'stream': fg_contents, 'mask': mask_contents, 'overlay': True}
        ])


    page.clean_contents()
    for xref in to_remove_xrefs:
        imgs = page.get_images(full=True)
        for img_data in imgs:
            if img_data[0] == xref:
                remove_images(doc, page, [img_data[7]])
    page.clean_contents()

    for insert in to_insert:
        img1 = insert[0]
        img2 = insert[1]
        page.insert_image(img1['bbox'], stream=img1['stream'],
                mask=img1['mask'], overlay=img1['overlay'], alpha=0)
        page.insert_image(img2['bbox'], stream=img2['stream'],
                mask=img2['mask'], overlay=img2['overlay'], alpha=0)
        #page.clean_contents()

    page.clean_contents()


def compress_pdf(pdf_input: str, pdf_output: str, hocr_iter = None):
    with fitz.open(pdf_input) as doc:

        for page in doc:
            if hocr_iter:
                hocr_page = next(hocr_iter)
                hocr_word_data = hocr_page_to_word_data(hocr_page)
            else:
                hocr_word_data = []

            compress_page_images(doc, page, hocr_word_data=hocr_word_data)

            page.clean_contents()

        doc.save(pdf_output, deflate=True, pretty=True, garbage=2)


if __name__ == '__main__':

    compress_pdf('../../dreamocr_debug_docs/debug_inputs/43.pdf.pdf', 'tmp.pdf')


