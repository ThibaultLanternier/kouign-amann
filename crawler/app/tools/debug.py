def record_thumbnail_to_html(base64_thumbnail: str, file_name: str):
    with open(f"{file_name}.html", "w") as f:
        f.write(
            f'<html><body><img src="data:image/jpeg;base64,{base64_thumbnail}"/><body/><html/>'
        )
