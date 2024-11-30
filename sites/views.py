import os
import zipfile
import shutil
from django.utils.text import slugify
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.static import serve
from .models import SiteArchive, Category
from .forms import SiteArchiveForm
from tempfile import TemporaryDirectory


def upload_archive(request):
    if request.method == 'POST':
        form = SiteArchiveForm(request.POST, request.FILES)
        if form.is_valid():
            site_archive = form.save()

            archive_path = site_archive.archive.path
            extract_to = os.path.join(settings.MEDIA_ROOT, 'extracted', str(site_archive.id))
            os.makedirs(extract_to, exist_ok=True)

            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)

            site_archive.extracted_path = extract_to
            site_archive.save()
            return redirect('view_site', site_id=site_archive.id)
    else:
        form = SiteArchiveForm()

    return render(request, 'index.html', {'form': form})


def view_site(request, category_slug, site_slug, path='index.html'):
    try:
        category = get_object_or_404(Category, slug=category_slug)
        site = get_object_or_404(SiteArchive, slug=site_slug, category=category)
        file_path = os.path.join(settings.MEDIA_ROOT, site.extracted_path, path)
        if not os.path.exists(file_path):
            raise Http404(f"{path} не найден.")

        if path.endswith('.html'):
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return HttpResponse(html_content)

        return serve(request, os.path.basename(file_path), os.path.dirname(file_path))
    except SiteArchive.DoesNotExist:
        raise Http404("Сайт не найден")


def download_archive(request, category_slug, site_slug):
    site = get_object_or_404(SiteArchive, slug=site_slug)

    # Создаем временную директорию для модифицированного архива
    with TemporaryDirectory() as temp_dir:
        modified_archive_path = os.path.join(temp_dir, f"{slugify(site.name)}_modified.zip")

        # Копируем файлы из распакованного архива
        extracted_path = os.path.join(settings.MEDIA_ROOT, site.extracted_path)

        # Создание нового архива с изменением содержимого
        with zipfile.ZipFile(modified_archive_path, 'w') as zipf:
            for root, dirs, files in os.walk(extracted_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, extracted_path)

                    # Изменение index.html
                    if file == "index.html":
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Вставка изменения в index.html
                        modified_content = content.replace(
                            '{{ unique_token }}',
                            f'{site.offer_web.unique_token}'
                        )

                        # Сохранение измененного index.html во временный файл
                        temp_index_path = os.path.join(temp_dir, "index.html")
                        with open(temp_index_path, 'w', encoding='utf-8') as temp_f:
                            temp_f.write(modified_content)

                        # Добавляем измененный файл в архив
                        zipf.write(temp_index_path, arcname=relative_path)
                    else:
                        # Добавляем остальные файлы без изменений
                        zipf.write(file_path, arcname=relative_path)

        # Отправка архива пользователю
        with open(modified_archive_path, 'rb') as archive_file:
            response = HttpResponse(archive_file.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{site.slug}_modified.zip"'
            return response