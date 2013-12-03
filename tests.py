import unittest
import POSIXlisp

def is_vector(form):
    return isinstance(form, POSIXlisp.Vector)

def is_list(form):
    return isinstance(form, POSIXlisp.List)

class TestSpecialForms(unittest.TestCase):

    def test_if(self):
        val = POSIXlisp.parse_eval("(if (= 1 1) 44 45)", POSIXlisp.create_base_env())
        self.assertEqual(val, 44)
        val = POSIXlisp.parse_eval("(if (= 1 0) 44 46)", POSIXlisp.create_base_env())
        self.assertEqual(val, 46)

    def test_quote(self):
        val = POSIXlisp.parse_eval("(quote (1 2 3))", POSIXlisp.create_base_env())
        self.assertEqual(val.__str__(), "(1 2 3)")
        self.assertTrue(is_list(val))

        val = POSIXlisp.parse_eval("(quote [1 2 3])", POSIXlisp.create_base_env())
        self.assertEqual(val.__str__(), "[1 2 3]")
        self.assertTrue(is_vector(val))

    def test_def(self):
        env = POSIXlisp.create_base_env()
        val = POSIXlisp.parse_eval("(def a 44)", env)
        self.assertEqual(val, POSIXlisp.Symbol("a"))
        val = POSIXlisp.parse_eval("a", env)
        self.assertEqual(val, 44)

    def test_fn(self):
        val = POSIXlisp.parse_eval("((fn [a] (+ 1 a)) 2)", POSIXlisp.create_base_env())
        self.assertEqual(val.__str__(), "3")

class TestFunctions(unittest.TestCase):

    def test_plus(self):
        val = POSIXlisp.parse_eval("(+ 1 1)", POSIXlisp.create_base_env())
        self.assertEqual(val, 2)

    def test_equals(self):
        val = POSIXlisp.parse_eval("(= 1 1)", POSIXlisp.create_base_env())
        self.assertEqual(val, True)
        val = POSIXlisp.parse_eval("(= 1 2)", POSIXlisp.create_base_env())
        self.assertEqual(val, False)

    def test_cons(self):
        val = POSIXlisp.parse_eval("(cons 1 (quote (2 3)))", POSIXlisp.create_base_env())
        self.assertEqual(val.__str__(), "(1 2 3)")
        self.assertTrue(is_list(val))

        val = POSIXlisp.parse_eval("(cons 1 [2 3])", POSIXlisp.create_base_env())
        self.assertEqual(val.__str__(), "[2 3 1]")
        self.assertTrue(is_vector(val))

    def test_first(self):
        val = POSIXlisp.parse_eval("(first (quote (1 2 3)))", POSIXlisp.create_base_env())
        self.assertEqual(val, 1)

        val = POSIXlisp.parse_eval("(first [1 2 3])", POSIXlisp.create_base_env())
        self.assertEqual(val, 1)

    def test_rest(self):
        val = POSIXlisp.parse_eval("(rest (quote (1 2 3)))", POSIXlisp.create_base_env())
        self.assertEqual(val.__str__(), "(2 3)")
        self.assertTrue(is_list(val))

        val = POSIXlisp.parse_eval("(rest [1 2 3])", POSIXlisp.create_base_env())
        self.assertEqual(val.__str__(), "[2 3]")
        self.assertTrue(is_vector(val))

class TestDataStructures(unittest.TestCase):

    def test_int(self):
        val = POSIXlisp.parse_eval("1", POSIXlisp.create_base_env())
        self.assertEqual(val, 1)

    def test_vector(self):
        val = POSIXlisp.parse_eval("[1 2 3]", POSIXlisp.create_base_env())
        self.assertEqual(val.__str__(), "[1 2 3]")

    def test_string(self):
        val = POSIXlisp.parse_eval("\"string\"", POSIXlisp.create_base_env())
        self.assertEqual(val, POSIXlisp.String("string"))

    def test_keyword(self):
        val = POSIXlisp.parse_eval(":keyword", POSIXlisp.create_base_env())
        self.assertEqual(val, POSIXlisp.Keyword(":keyword"))

if __name__ == '__main__':
    unittest.main()
