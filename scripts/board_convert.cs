using System.IO;
using System.Text.RegularExpressions;

// Check for correct usage
if (args.Length < 2)
{
    Console.WriteLine("Error: Missing arguments.");
    Console.WriteLine("Usage: dotnet run -- <input_file_path> <output_file_path>");
    return;
}

string inputPath = args[0];
string outputPath = args[1];

// Verify input file exists
if (!File.Exists(inputPath))
{
    Console.WriteLine($"Error: Input file not found at '{inputPath}'");
    return;
}

// 1. Load the file content into the text variable
string text = File.ReadAllText(inputPath);

// 2. Regex Operations

// Replace lines starting with # with <hr/>
// RegexOptions.Multiline ensures ^ and $ match start/end of lines, not just start/end of string
text = Regex.Replace(text, @"^#.*$", "<hr/>", RegexOptions.Multiline);

// Replace italics *text* with [i]text[/i]
text = Regex.Replace(text, @"\*(.+?)\*", "[i]$1[/i]");

// Replace \! with !
text = Regex.Replace(text, @"\\!", "!");

// 3. Write result to output file
try 
{
    File.WriteAllText(outputPath, text);
    Console.WriteLine($"Successfully converted '{inputPath}' to '{outputPath}'");
}
catch (Exception ex)
{
    Console.WriteLine($"Error writing output: {ex.Message}");
}