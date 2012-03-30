
class ISBN:
    def __init__(self,isbn):
        self.isbn = isbn
        self.strip()

    def strip(self):
        """Strip whitespace, hyphens, etc. from an ISBN number and return the result."""
        self.isbn = filter(lambda x: str.isdigit(x) or x.upper() == "X", self.isbn)

    def convert(self):
        """Convert an ISBN-10 to ISBN-13 or vice-versa."""

        if not self.valid():
            raise ValueError("Invalid ISBN")

        if len(self.isbn) == 10:
            stem = "978" + self.isbn[:-1]
            self.isbn = stem + self.check(stem)
        else:
            if self.isbn.startswith("978"):
                stem = self.isbn[3:-1]
                self.isbn = stem + self.check(stem)
            else:
                raise ValueError("ISBN not convertible")

    def valid(self):
        """Check the validity of an ISBN. Works for either ISBN-10 or ISBN-13."""

        if len(self.isbn) == 10:
            return self.valid_isbn10()
        if len(self.isbn) == 13:
            return self.valid_isbn13()
        return False

    def check(self,short):
        """Compute the check digit for the stem of an ISBN. Works with either the
        first 9 digits of an ISBN-10 or the first 12 digits of an ISBN-13."""

        if len(short) == 9:
            return self.check_isbn10(short)
        if len(short) == 12:
            return self.check_isbn13(short)
        return False

    def check_isbn10(self,stem):
        """Computes the ISBN-10 check digit based on the first 9 digits of a
        stripped ISBN-10 number."""

        check = 11 - sum( (x+2) * int(y) for x,y in enumerate(reversed(stem)) ) % 11
        if check == 10:
            return "X"
        elif check == 11:
            return "0"

        return str(check)

    def valid_isbn10(self):
        """Checks the validity of an ISBN-10 number."""

        short = self.isbn
        if len(short) != 10:
            return False

        digits = [ (10 if x.upper() == "X" else int(x)) for x in short ]
        return (sum( (x+1)*y for x,y in enumerate(reversed(digits)) ) % 11) == 0

    def check_isbn13(self,stem):
        """Compute the ISBN-13 check digit based on the first 12 digits of a
        stripped ISBN-13 number. """

        check = 10 - sum( (x%2*2+1) * int(y) for x,y in enumerate(stem) ) % 10
        if check == 10:
            return "0"

        return str(check)

    def valid_isbn13(self):
        """Checks the validity of an ISBN-13 number."""

        short = self.isbn
        if len(short) != 13:
            return False

        digits = [ (10 if x.upper() == "X" else int(x)) for x in short ]
        return (sum( (x%2*2+1) * y for x,y in enumerate(digits) ) % 10) == 0

    def to_isbn10(self):
        """Converts supplied ISBN (either ISBN-10 or ISBN-13) to a stripped ISBN-10."""

        if not self.valid():
            raise ValueError("Invalid ISBN")

        if not self.valid_isbn10():
            self.convert()

    def to_isbn13(self):
        """Converts supplied ISBN (either ISBN-10 or ISBN-13) to a stripped ISBN-13."""

        if not self.valid():
            raise ValueError("Invalid ISBN")

        if not self.valid_isbn13():
            self.convert()

    def format(self, sep=""):
        s = self.isbn

        if len(s) == 10:
            return s[0] + sep + s[1:6] + sep + s[6:9] + sep + s[9]

        if len(s) == 13:
            return s[0:3] + sep + s[3:9] + sep + s[9:12] + sep + s[12]


if __name__ == '__main__':

    validisbn10 = ISBN('0201633612')
    validisbn13 = ISBN('978-0201633610')

    print 'isbn10'
    print validisbn10.format('-')
    validisbn10.to_isbn13()
    print validisbn10.format('-')

    print 'isbn13'
    print validisbn13.format('-')
    validisbn13.to_isbn13()
    print validisbn13.format('-')
    
    invalidisbn = ISBN('1239')
    print invalidisbn.format('-')
    invalidisbn.convert()
    print invalidisbn.format('-')
