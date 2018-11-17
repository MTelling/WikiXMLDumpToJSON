import os
import click
import json

from WikiReader import WikiReader

INDEX_FILE_NAME = 'index.json'
SITEINFO_FILE_NAME = 'siteinfo.json'
FILE_NAME_FORMAT = "{}_{}.json"


def write_to_json_file(obj, path, name):
    with open(os.path.join(path, name), 'w+', encoding='utf-8') as file:
        text = json.dumps(obj, ensure_ascii=False)
        file.write(text)


def get_file_name_containing_page(page_title, index, file_suffix):
    if page_title in index:
        return FILE_NAME_FORMAT.format(index[page_title], file_suffix)
    else:
        return None


def load_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def __get_page(page_title, path_to_files, file_suffix, index):
    page_file_name = get_file_name_containing_page(page_title, index, file_suffix)
    if not page_file_name:
        return None

    page_file = load_json_file(os.path.join(path_to_files, page_file_name))
    for page in page_file:
        if page['title'] == page_title:
            return page

    return None


@click.group()
def cli():
    pass

@click.command()
@click.option('--page-title', prompt='Page to retrieve')
@click.option('--path-to-files', prompt='Path to wikipedia json files')
@click.option('--file-suffix', default='wiki_part',
              help="The suffix for the splitted json files. Fx wiki_part")
def get_page(page_title, path_to_files, file_suffix):
    index = load_json_file(os.path.join(path_to_files, INDEX_FILE_NAME))
    page = __get_page(page_title, path_to_files, file_suffix, index)
    click.echo(page)
    return page

@click.command()
@click.option('--pages_file', prompt="Path to requested pages file")
@click.option('--path-to-files', prompt='Path to wikipedia json files')
@click.option('--file-suffix', default='wiki_part',
              help="The suffix for the splitted json files. Fx wiki_part")
@click.option('--output-folder', prompt="Path to output folder",
              help="Path to output folder")
@click.option('--output-file-name', default='data.json')
@click.option('--missed-files-file-name', default='missed_pages.json')
def get_pages(pages_file, path_to_files, file_suffix, output_folder, output_file_name, missed_files_file_name):
    pages = []
    not_found = []
    index = load_json_file(os.path.join(path_to_files, INDEX_FILE_NAME))
    with open(pages_file, 'r') as f:
        for page_title in f:
            page_title = page_title.strip().replace("\n", "")
            page = __get_page(page_title, path_to_files, file_suffix, index)
            if page:
                click.echo("Page '{}' written to file!".format(page_title))
                pages.append(page)
            else:
                not_found.append(page_title)
                click.echo("Could not find file: {}!".format(page_title))

    write_to_json_file(pages, output_folder, output_file_name)
    if len(not_found) > 0:
        write_to_json_file(not_found, output_folder, missed_files_file_name)

@click.command()
@click.option('--pages-per-part', default=100,
              help='Number of pages for each output file after split.')
@click.option('--input-file', prompt='Path to wiki xml file',
              help="Path to the multi-stream xml file containing Wiki data.")
@click.option('--output-folder', prompt='Path to folder to store output files',
              help="Path to the folder where the output files should be placed.")
@click.option('--output-file-suffix', default='wiki_part',
              help="The suffix for the split file. Fx wiki_part")
def split_wiki(pages_per_part, input_file, output_folder, output_file_suffix):
    click.echo("The wikipedia file '{}' will now be split into "
               "several files each of '{}' pages.".format(input_file, pages_per_part))
    click.echo("This process might take a while!")

    wiki_reader = WikiReader(input_file)
    index = {}

    # Write the site info to its own file
    write_to_json_file(wiki_reader.site_info, output_folder, SITEINFO_FILE_NAME)

    # Go over all pages and write them into files of about split_size_kb
    current_pages = []
    current_count = 0
    for page in wiki_reader:
        current_pages.append(page)
        index[page['title']] = current_count
        if len(current_pages) > pages_per_part:
            write_to_json_file(
                current_pages,
                output_folder,
                FILE_NAME_FORMAT.format(current_count, output_file_suffix)
            )
            current_pages = []
            current_count += 1
            print("Processed {} articles!".format(current_count * pages_per_part))

    if len(current_pages) != 0:
        write_to_json_file(
            current_pages,
            output_folder,
            FILE_NAME_FORMAT.format(current_count, output_file_suffix)
        )

    write_to_json_file(index, output_folder, INDEX_FILE_NAME)


if __name__ == '__main__':
    cli.add_command(split_wiki)
    cli.add_command(get_page)
    cli.add_command(get_pages)
    cli()


