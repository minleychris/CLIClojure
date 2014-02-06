import unittest
import CLIClojure
import clojure.lang


def is_vector(form):
    return isinstance(form, CLIClojure.Vector)


def is_seq(form):
    return isinstance(form, clojure.lang.ISeq)


def eval_one(s, ns=None):
    return eval_all(s, ns)[0]


def eval_all(s, ns=None):
    if ns is None:
        ns = CLIClojure.create_base_ns()
    return CLIClojure.parse_eval(s, ns)


class TestSpecialForms(unittest.TestCase):

    def test_if(self):
        val = eval_one("(if (= 1 1) 44 45)")
        self.assertEqual(val, 44)
        val = eval_one("(if (= 1 0) 44 46)")
        self.assertEqual(val, 46)

    def test_quote(self):
        val = eval_one("(quote (1 2 3))")
        self.assertEqual(val.__str__(), "(1 2 3)")
        self.assertTrue(is_seq(val))

        val = eval_one("(quote [1 2 3])")
        self.assertEqual(val.__str__(), "[1 2 3]")
        self.assertTrue(is_vector(val))

    def test_def(self):
        ns = CLIClojure.create_base_ns()
        val = eval_one("(def a 44)", ns)
        self.assertEqual(val, CLIClojure.Symbol.intern("a"))
        val = eval_one("a", ns)
        self.assertEqual(val, 44)

    def test_fn(self):
        val = eval_one("((fn* [a] (+ 1 a)) 2)")
        self.assertEqual(val.__str__(), "3")

    def test_let(self):
        val = eval_one("(let* [a 1] (+ a 1))")
        self.assertEqual(val.__str__(), "2")
        val = eval_one("(let* [a 1 b (+ a 1)] (+ b 1))")
        self.assertEqual(val.__str__(), "3")

    def test_do(self):
        ns = CLIClojure.create_base_ns()
        val = eval_one("(do (def a 44) 4)", ns)
        self.assertEqual(val, 4)
        val = eval_one("a", ns)
        self.assertEqual(val, 44)

    def test_ns(self):
        ns = CLIClojure.create_base_ns()
        val = eval_one("(ns clojure.core)", ns)
        val = eval_one("(+ 1 1)", val)
        self.assertEqual(val, 2)

        val = eval_one("(ns test)", ns)
        val = eval_one("+", val)
        self.assertEqual(val, None)  # TODO: Should be exception

    def test_comment(self):
        ns = CLIClojure.create_base_ns()
        val = eval_one("(comment test)", ns)
        self.assertEqual(val, None)


class TestFunctions(unittest.TestCase):

    def test_plus(self):
        val = eval_one("(+ 1 1)")
        self.assertEqual(val, 2)

    def test_equals(self):
        val = eval_one("(= 1 1)")
        self.assertEqual(val, True)
        val = eval_one("(= 1 2)")
        self.assertEqual(val, False)

    def test_first(self):
        val = eval_one("(first (quote (1 2 3)))")
        self.assertEqual(val, 1)

        val = eval_one("(first [1 2 3])")
        self.assertEqual(val, 1)

    def test_rest(self):
        val = eval_one("(rest (quote (1 2 3)))")
        self.assertEqual(val.__str__(), "(2 3)")
        self.assertTrue(is_seq(val))

        val = eval_one("(rest [1 2 3])")
        self.assertEqual(val.__str__(), "[2 3]")
        self.assertTrue(is_vector(val))

    def test_meta(self):
        val = eval_one("(meta [1 2 3])")
        self.assertEqual(val, None)

        val = eval_one("(meta (with-meta [1 2 3] \"x\"))")
        self.assertEqual(val.__str__(), "x")


class TestDataStructures(unittest.TestCase):

    def test_int(self):
        val = eval_one("1")
        self.assertEqual(val, 1)

    def test_vector(self):
        val = eval_one("[1 2 3]")
        self.assertEqual(val.__str__(), "[1 2 3]")

    def test_string(self):
        val = eval_one("\"string\"")
        self.assertEqual(val, "string")

    def test_keyword(self):
        val = eval_one(":keyword")
        self.assertEqual(val, CLIClojure.Keyword(":keyword"))

    def test_boolean(self):
        val = eval_one("true")
        self.assertEqual(val, True)

        val = eval_one("false")
        self.assertEqual(val, False)

    def test_nil(self):
        val = eval_one("nil")
        self.assertEqual(val, None)

    def test_map(self):
        val = eval_one("{:a 1}")
        self.assertEqual(val.__str__(), "{:a 1}")

        val = eval_one("{:a 1 :b 2}")
        self.assertEqual(val.__str__(), "{:a 1, :b 2}")


class TestReaderMacros(unittest.TestCase):

    def test_comment(self):
        val = eval_all(";a")
        self.assertEqual(len(val), 0)

        val = eval_all("(+ 1 1) ;a")
        self.assertEqual(val[0], 2)
        self.assertEqual(len(val), 1)

        val = eval_all(";a (+ 1 1)")
        self.assertEqual(len(val), 0)

        val = eval_all(";a\n (+ 1 1)")
        self.assertEqual(val[0], 2)
        self.assertEqual(len(val), 1)

    def test_quote(self):
        val = eval_one("'(1 2 3)")
        self.assertEqual(val.__str__(), "(1 2 3)")
        self.assertTrue(is_seq(val))

        val = eval_one("'[1 2 3]")
        self.assertEqual(val.__str__(), "[1 2 3]")
        self.assertTrue(is_vector(val))

    def test_metadata(self):
        val = eval_one("(meta ^{:test true} [1 2 3])")
        self.assertEqual(val.get(clojure.lang.Keyword("test")), True)

        val = eval_one("(meta ^:test [1 2 3])")
        self.assertEqual(val.get(clojure.lang.Keyword("test")), True)

        val = eval_one("(meta ^\"test\" [1 2 3])")
        self.assertEqual(val.get(clojure.lang.Keyword("tag")), "test")


class TestClojureDefinedFunctions(unittest.TestCase):

    def test_list(self):
        val = eval_one("(list 1 2 3)")
        self.assertEqual(val.__str__(), "(1 2 3)")

    def test_cons(self):
        val = eval_one("(cons 1 (quote (2 3)))")
        self.assertEqual(val.first(), 1)
        self.assertEqual(val.next().first(), 2)
        self.assertEqual(val.next().next().first(), 3)
        self.assertTrue(is_seq(val))

        val = eval_one("(cons 1 [2 3])")
        self.assertEqual(val.first(), 1)
        self.assertEqual(val.next().first(), 2)
        self.assertEqual(val.next().next().first(), 3)
        self.assertTrue(is_seq(val))

    def test_let(self):
        val = eval_one("(let [a 1] (+ a 1))")
        self.assertEqual(val.__str__(), "2")
        val = eval_one("(let [a 1 b (+ a 1)] (+ b 1))")
        self.assertEqual(val.__str__(), "3")


if __name__ == '__main__':
    unittest.main()
