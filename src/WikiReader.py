from xml.etree import ElementTree


class WikiReader:

    @staticmethod
    def __clean_tag(tag):
        """
        Tags look like '{http://www.mediawiki.org/xml/export-0.10/}mediawiki'
        We are not interested in the first part of this, so we only take what's }
        """
        splitted_tag = tag.split("}")
        if len(splitted_tag) == 1:
            print("Found tag with no }: {}".format(tag))
            return ""
        else:
            return splitted_tag[-1]

    def __init__(self, wiki_file_path):
        self.__wiki_file_path = wiki_file_path
        self.__wiki_iterator = iter(ElementTree.iterparse(self.__wiki_file_path, events=('start', 'end')))
        event, self.__root = next(self.__wiki_iterator)
        tag = self.__clean_tag(self.__root.tag)
        if not tag == 'mediawiki':
            raise Exception("Unexpected root tag: {}. Expected 'mediawiki'!".format(tag))

        self.site_info = self.__read_site_info()

    def __del__(self):
        if self.__root:
            self.__root.clear()

    def __iter__(self):
        return self

    def __read_site_info(self):
        """
        Reads the site info from top of Wiki XML into dictionary
        :return: siteinfo as dictionary
        """
        event, root = next(self.__wiki_iterator)
        tag = self.__clean_tag(root.tag)
        if tag != 'siteinfo':
            return None
        else:
            return self.__tree_to_dict(root, tag, ['namespaces'])

    def __skip_element(self, root):
        root_tag = self.__clean_tag(root.tag)
        event = tag = ''
        while event != 'end' or tag != root_tag:
            event, elem = next(self.__wiki_iterator)
            tag = self.__clean_tag(elem.tag)
        root.clear()

    def __get_next_page_root(self):
        # Read until we meet a page
        skip_count = 0
        for event, root in self.__wiki_iterator:
            root_tag = self.__clean_tag(root.tag)

            if root_tag == 'page':
                return root, root_tag

            # If we did not meet a page, skip the current element
            print("Met something that was not a page. It was {}".format(root_tag))
            self.__skip_element(root)
            skip_count += 1
            if skip_count > 100:
                raise Exception("After 100 skipped elements, still no page has been found")

    def __next__(self):
        """
        Reads the next page from XML stream into dictionary
        :return: page in dictionary form
        """
        root, root_tag = self.__get_next_page_root()
        return self.__tree_to_dict(root, root_tag, ['revision', 'contributor'])

    def __element_text(self, element):
        """
        An element might have text on both start and end element.
        So we need to iterate over this to find all text for a given element.
        """
        result = element.text if element.text else ''
        for event, element in self.__wiki_iterator:
            if element.text and result != element.text:
                result += element.text
            if event == 'end':
                break
        return result

    def __tree_to_dict(self, root, root_tag, nested_tags):
        tags = ['']
        layers = [{}]
        for event, element in self.__wiki_iterator:
            tag = self.__clean_tag(element.tag)
            if event == 'end' and tag == root_tag:
                root.clear()
                return layers[0]

            if event == 'start':
                # If a tag is nested it means it has children,
                # so we create a new layer for the children
                if tag in nested_tags:
                    # We move to a new layer
                    tags.append(tag)
                    layers.append({})
                else:
                    # Read values into current layer
                    if len(element.attrib) > 0 and tag != 'text':
                        # If there are attributes to the element include these
                        contents = {}
                        if 'key' in element.attrib:
                            contents['#tag'] = tag
                            tag = element.attrib['key']
                            del element.attrib['key']

                        if element.text:
                            contents['#text'] = self.__element_text(element)
                        contents.update(element.attrib)
                        layers[-1][tag] = contents
                    else:
                        if tag in layers[-1]:
                            raise Exception("Tag already seen! {} with title {}".format(tag, layers[0]['title']))
                        layers[-1][tag] = self.__element_text(element)

            elif event == 'end':
                if tag == tags[-1]:
                    # We move a layer out
                    last_dict = layers.pop()
                    layers[-1][tags.pop()] = last_dict

        root.clear()
        return layers[0]
