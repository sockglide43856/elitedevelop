import qrcode
import base64
from io import BytesIO
from django.shortcuts import render

def generate_qr_view(request):
    context = {}

    if request.method == "POST":
        # Capture customization inputs from the front-end form
        qr_data = request.POST.get("qr_data", "https://elitedevelop.pythonanywhere.com")
        fill_color = request.POST.get("fill_color", "#000000")
        back_color = request.POST.get("back_color", "#ffffff")
        box_size = int(request.POST.get("box_size", 10))
        border_size = int(request.POST.get("border_size", 4))

        try:
            # 1. Initialize the customized QR Engine
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H, # High error tolerance
                box_size=box_size,
                border=border_size,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            # 2. Compile image using the custom user color profiles
            img = qr.make_image(fill_color=fill_color, back_color=back_color)

            # 3. Stream to memory buffer (Uses 0 bytes of disk storage!)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            # 4. Encode to Base64 data URI string for easy injection into HTML <img> tags
            image_png = buffer.getvalue()
            graphic = base64.b64encode(image_png).decode('utf-8')

            # Pack values back into context to keep form persistence seamless
            context['qr_code'] = f"data:image/png;base64,{graphic}"
            context['qr_data'] = qr_data
            context['fill_color'] = fill_color
            context['back_color'] = back_color
            context['box_size'] = box_size
            context['border_size'] = border_size

        except Exception as e:
            context['error'] = f"Generation anomaly detected: {e}"

    else:
        # Default fallback values for first-page hit lifecycle
        context['fill_color'] = '#000000'
        context['back_color'] = '#ffffff'
        context['box_size'] = 10
        context['border_size'] = 4

    return render(request, "generator.html", context)