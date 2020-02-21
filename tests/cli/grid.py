import unittest
import subprocess
from os import path, remove

from px2ph.utils.yaml import get_yaml


class GridTest(unittest.TestCase):
    def setUp(self):
        self.input_path = 'tests/resources/gridOpts.yml'
        self.output_path = get_yaml(self.input_path)['output']

    def test_grid_generation(self):
        process = subprocess.run([
            'python3', '-m', 'px2ph.tools.grid',
            '-c', self.input_path
        ])
        self.assertEqual(0, process.returncode)
        self.assertTrue(path.isfile(self.output_path))

    def tearDown(self):
        remove(self.output_path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
