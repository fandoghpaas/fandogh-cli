import unittest


class WorkSpaceTestCase(unittest.TestCase):

    def test_adding_custom_folder_to_ignore_files(self):
        from fandogh_cli.workspace import Workspace
        custom_entries = ["folder{}".format(i) for i in range(5)]
        ignore_folders = ["behrooz", "git", ".git"]
        expected_list = custom_entries + ignore_folders
        entries = Workspace.add_custom_ignore_folder_to_entries(entries=custom_entries, ignore_folders=ignore_folders)
        self.assertEqual(entries, expected_list)

    def test_adding_custom_folder_when_they_already_in_files(self):
        from fandogh_cli.workspace import Workspace
        custom_entries = ["folder{}".format(i) for i in range(5)]
        ignore_folders = ["behrooz", "git", ".git", "behrooz", "behrooz", "behrooz", "behrooz", "something"]
        unique_ignore_folders = list(dict.fromkeys(ignore_folders))
        expected_list = custom_entries + unique_ignore_folders
        entries = Workspace.add_custom_ignore_folder_to_entries(entries=custom_entries, ignore_folders=ignore_folders)
        self.assertEqual(entries, expected_list)


if __name__ == '__main__':
    unittest.main()
