// Copyright (c) 2012 The Khronos Group Inc.// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to // the following conditions: // The above copyright notice and this permission notice shall be included // in all copies or substantial portions of the Materials. // THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

using System;
using System.Xml;
using System.Xml.Schema;
using System.Collections;
using System.IO;

namespace SchemaValidate
{
	class SchemaValidate
	{
        private static bool isValid = true;
        private static ArrayList list = new ArrayList(); // strings
        private static bool encounteredFatalError = false;
        private static Exception fatalError = null;

        public static void MyValidationEventHandler(object sender,
            ValidationEventArgs args)
        {
            if (args.Severity == XmlSeverityType.Error)
            {
                isValid = false;
            }
            list.Add(args.Severity + ": " + args.Message);
        }

		[STAThread]
		static void Main(string[] args)
        {
            if (args.Length != 4) 
            {
                Console.WriteLine("Invalid parameter count. Exiting...");
                return;
            }

            string xmlFile = args[0];
            string xdsFile = args[1];
            string xdsNamespace = args[2];
            string outputFile = args[3];

            try
            {
                XmlSchemaCollection cache = new XmlSchemaCollection();
                cache.Add(xdsNamespace, xdsFile);

                XmlTextReader r = new XmlTextReader(xmlFile);
                XmlValidatingReader v = new XmlValidatingReader(r);
                v.Schemas.Add(cache);

                v.ValidationType = ValidationType.Schema;
                
                v.ValidationEventHandler +=
                    new ValidationEventHandler(MyValidationEventHandler);
                
                while (v.Read()) { } // look for validation errors
                v.Close();
            }
            catch (Exception e)
            {
                encounteredFatalError = true;
                fatalError = e;
            }
            
            StreamWriter file = new StreamWriter(outputFile);
            
            if (isValid && !encounteredFatalError)
                file.WriteLine("PASSED: Document is valid");
            else
                file.WriteLine("FAILED: Document is invalid");

            // Printing
            foreach (string entry in list)
            {
                file.WriteLine(entry);
            }
            if (encounteredFatalError)
            {
                file.WriteLine("Error: a FATAL error has occured " +
                        "while reading the file.\r\n" + fatalError.ToString());
            }
            file.Close();
		}
	}
}
