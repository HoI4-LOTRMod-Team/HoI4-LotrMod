using System.IO;

using System.Text.RegularExpressions;


void FixIDS()
{
    string dir = @"C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\history\countries";

    string[] files = Directory.GetFiles(dir, "*.txt");

    foreach (string file in files)
    {
        try
        {
            string content = File.ReadAllText(file);

            Regex rx = new Regex(@"capital\s*=\s*(\d+)", RegexOptions.Multiline);

            int id = int.Parse(rx.Match(content).Groups[1].ToString());

            id -= 741;

            content = Regex.Replace(content, @"capital\s*=\s*(\d+)", "capital = " + id);

            File.WriteAllText(file, content);
        }
        catch { Console.WriteLine(file); }
    }
}

FixIDS();
