import sys
import os
import getopt

import disunity

class SerializeTest(disunity.SerializedFileApp):

    def __init__(self):
        super(SerializeTest, self).__init__()

        self.num_files_passed = 0
        self.num_files_failed = 0
        self.num_objects_passed = 0
        self.num_objects_failed = 0
        self.num_objects_typeless = 0
        self.num_types_added = 0

        self.update_type_db = False
        self.deserialize = False
        self.signature = None

    def parse_args(self, argv):
        try:
            opts, argv = getopt.getopt(argv, 'du', ["deserialize", "update-db"])
        except getopt.GetoptError as e:
            print("Error:", e, file=sys.stderr)
            return False

        for o, a in opts:
            if o in ("-d", "--deserialize"):
                self.deserialize = True
            elif o in ("-u", "--update-db"):
                self.update_type_db = True

        return len(argv) > 0

    def usage(self):
        print("Usage: %s [OPTION...] [FILE...]" % os.path.basename(self.path))
        print("Performs various tests on serialized Unity files.")
        print()
        print("  -d, --deserialize          deserialize all objects")
        print("  -u, --update-db            update database with embedded types")

    def main(self, argv):
        if super(SerializeTest, self).main(argv):
            return

        print()
        print("Files passed:     %d" % self.num_files_passed)
        print("Files failed:     %d" % self.num_files_failed)

        if self.deserialize:
            print("Objects passed:   %d" % self.num_objects_passed)
            print("Objects failed:   %d" % self.num_objects_failed)
            print("Objects typeless: %d" % self.num_objects_typeless)

        if self.update_type_db:
            print("Types added:      %d" % self.num_types_added)

    def process(self, path):
        try:
            super(SerializeTest, self).process(path)
        except Exception:
            self.log.exception("Failed reading " + path)
            self.num_files_failed += 1

    def process_archive(self, path, archive):
        self.signature = archive.header.unity_revision
        super(SerializeTest, self).process_archive(path, archive)
        self.signature = None

    def process_serialized(self, path, sf):
        print(path)

        if self.update_type_db:
            self.num_types_added += sf.update_type_db(self.signature)

        if self.deserialize:
            print("% -16s  % -24s  %s" % ("Path", "Class", "Name"))
            for path_id in sf.objects:
                try:
                    object = sf.read_object(path_id)
                    if not object:
                        self.num_objects_typeless += 1
                        continue

                    class_name = object.__class__.__name__
                    print("%016x  % -24s  %s" % (path_id, class_name, object))

                    self.num_objects_passed += 1
                except Exception:
                    self.log.exception("Failed deserialization for path ID %d", path_id)
                    self.num_objects_failed += 1

        self.num_files_passed += 1

if __name__ == "__main__":
    sys.exit(SerializeTest().main(sys.argv))
