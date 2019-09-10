#!/usr/bin/python2

#
# (C) 2016 Jaguar Land Rover
# (C) 2019 GENIVI Alliance
#
# All files and artifacts in this repository are licensed under the
# provisions of the license provided by the LICENSE file in this repository.
#
#
# Convert vspec file to FrancaIDL spec.
#

import sys
import vspec
import json
import getopt

def usage():
    print "Usage:", sys.argv[0], "<-p package> <-m subtree_match>  <-n top-interface> [-I include_dir] ... [-i prefix:id_file] vspec_file franca_file"
    print "  -I include_dir       Add include directory to search for included vspec"
    print "                       files. Can be used multiple timees."
    print 
    print "  -i prefix:uuid_file  File to use for storing generated UUIDs for signals with"
    print "                       a given path prefix. Can be used multiple times to store"
    print "                       UUIDs for signal sub-trees in different files."
    print "  -p package           Fully qualified package name (should be a subset of the path name in VSS) (mandatory)"
    print "  -m subtree_match     subtree_match (should be the parent node at the tree level that is being generated) (mandatory)"
    print "  -n interface         Interface name  (should be the parent node at the tree level that is being generated) (mandatory)"
    print
    print " vspec_file            The vehicle specification file to parse."
    print " franca_file           The file to output the Franca IDL spec to."
    sys.exit(255)


def traverse_tree(tree, path_match, package_name, interface_name, outf, prefix_arr, is_first_element):
    # Convert a prefix array of path elements to a string
    def prefix_to_string(prefix_arr):
        if len(prefix_arr) == 0:
            return ""

        res = prefix_arr[0]
        for elem in prefix_arr[1:]:
            res = "{}.{}".format(res, elem)

        return res

#    print "path_match is {}".format(path_match)

    # Traverse all elemnts in tree.
    for key, val in tree.items():

        # Is this a branch?
        if "children" in val:
            # Yes. Recurse
            #traverse_tree(val['children'], path_match, outf, prefix_arr + [ key ], is_first_element)
            # Changed, check this
            traverse_tree(val['children'], path_match, package_name, interface_name, # branch name 
                    outf, prefix_arr + [ key ], is_first_element)
            continue

        # Drop a comma in before the next element.
        if not is_first_element:
            outf.write(",\n")

# Generate Franca attributes
# Types are for now just written as-is from the VSS (might need
# translation)

        fqn = prefix_to_string(prefix_arr + [ key ])

        #

        #print "** Comparing {} to {}\n".format(fqn, path_match)
        if fqn.startswith(path_match) :
            print "-----"
            #remove_part = prefix_to_string(prefix_arr+[key]).replace(interface_name+".",'')
            #print "Part to remove is {}".format(remove_part)

            attr_name = key
            prefix_str = prefix_to_string(prefix_arr)
            # than one subtree - then prefix is needed on the
            # attribute name
            #partly_qualified_name = fqn.replace(remove_part,'');
            print "prefix_str is {}".format(prefix_str)
            partly_qualified_name = fqn
#            partly_qualified_name = partly_qualified_name.replace(prefix_str+".",'')
#            partly_qualified_name = partly_qualified_name.replace(match_pattern+".",'')
            partly_qualified_name = partly_qualified_name.replace(package_name+"."+interface_name+".",'')

            print "### interface_name is {}\n ### attr_name is {}\n### path_match is {}\n### pqn is {}\n".format(interface_name, attr_name, path_match, partly_qualified_name)
            print "### pqn is {}".format(partly_qualified_name)
            print "### fqn is {}".format(fqn)
            print "-----"

            outf.write("   attribute {0:} {1:<30} /* {2:} */ \n".format(val['datatype'],
                partly_qualified_name, fqn))
        else:
#            print("Skipping non-matching VSS signal {}".format(fqn))
            x = "a"


if __name__ == "__main__":
    #
    # Check that we have the correct arguments
    #
    opts, args= getopt.getopt(sys.argv[1:], "I:i:v:p:n:m:")

    # Always search current directory for include_file
    vss_version = "unspecified version"
    include_dirs = ["."]
    package_name = interface_name = None
    for o, a in opts:
        if o == "-I":
            include_dirs.append(a)
        elif o == "-v":
            vss_version = a
        elif o == "-i":
            id_spec = a.split(":")
            if len(id_spec) != 2:
                print("ERROR: -i needs a 'prefix:uuid_file' argument.")
                usage()

            [prefix, file_name] = id_spec
            vspec.db_mgr.create_signal_uuid_db(prefix, file_name)
        elif o == "-p":
            package_name = a
        elif o == "-n":
            interface_name = a
        elif o == "-m":
            match_pattern = a
        else:
            usage()

    if package_name == None:
        print "MUST USE -p!"
        usage()

    if interface_name == None:
        print "MUST USE -n!"
        usage()

    if len(args) != 2:
        usage()

    franca_out = open (args[1], "w")
    try:
        tree = vspec.load(args[0], include_dirs)
    except vspec.VSpecError as e:
        print("Error: {}".format(e))
        exit(255)

    franca_out.write(
"""// Copyright (C) 2019 
// Contributors to Vehicle Signal Specification
// (https://gitub.com/GENIVI/vehicle_signal_specification)
//
// This program is licensed under the terms and conditions of the
// Mozilla Public License, version 2.0.  The full text of the
// Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

const UTF8String VSS_VERSION = "{}"

// Vehicle signal attributes generated from VSS specification version FIXME

package {} {{

  interface {} {{

""".format(vss_version, package_name, interface_name))

    #traverse_tree(tree, "{}.{}".format(package_name, interface_name), franca_out, [], True)
    traverse_tree(tree, match_pattern, package_name, interface_name, franca_out, [], True)
    franca_out.write("  }\n")
    franca_out.write("}\n")

    franca_out.write("""
// End of file
""")

    franca_out.close()

