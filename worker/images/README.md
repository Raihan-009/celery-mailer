# Email Images

This directory contains the images used in email templates.

## Required Images

Place the following images in this directory:

1. **logo.png** - The Poridhi company logo (113x32 pixels recommended)
2. **success_icon.png** - Success checkmark icon (120x120 pixels recommended)

## Image Requirements

- **Format**: PNG, JPG, or GIF
- **Size**: Keep file sizes reasonable for email (under 100KB each)
- **Dimensions**: 
  - Logo: 113x32 pixels (or similar aspect ratio)
  - Success icon: 120x120 pixels (square)

## How it works

The images are attached as inline attachments with Content-ID (CID) references:
- `logo.png` → `cid:logo`
- `success_icon.png` → `cid:success_icon`

The HTML template uses these CID references instead of external URLs, ensuring the images display even when external resources are blocked by email clients.

## Adding New Images

To add new images:

1. Place the image file in this directory
2. Update the `image_files` dictionary in `mailer.py`:
   ```python
   image_files = {
       "logo": "logo.png",
       "success_icon": "success_icon.png",
       "new_image": "new_image.png"  # Add your new image here
   }
   ```
3. Use `cid:new_image` in your HTML template
