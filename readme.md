# 💼 LinkedIn AI Apply Bot

A Python bot that automatically applies to all **LinkedIn “Easy Apply” jobs** based on your CV — secure, fast, and fully customizable.

---

## ⚙️ Installation 🔌

1. **Clone the repository**
   ```bash
   git clone https://github.com/danielfnz/linkedin-ia-applier
   cd linkedin-ia-applier
   ```

2. **Make sure Python3 and pip3 are installed**

3. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Configure your settings**
   - Enter your **LinkedIn credentials** on lines **1 and 2** of the `config.py` file  
   - Add your **OpenAI API key** on line **3**  
   - Adjust the remaining settings according to your preferences (filters, location, keywords, etc.)

5. **Save your cv**
  - Save your CV in a root folder
  - Add your **cv_file_name patch** on line **4**  

6. **Run the bot**
   ```bash
   python3 main.py
   ```

---

## 💡 Features

- Filter jobs by:
  - **Easy Apply**
  - **Location** (Worldwide, Europe, Poland, etc.)
  - **Keyword** (*Python*, *React*, *Node*, etc.)
  - **Experience level**, **position**, **job type**, and **date posted**
- Apply based on your **salary preferences** (works best for U.S. job listings)
- Automatically **apply to matching jobs**
- Optionally **follow companies** after successful applications
- **Runs silently in the background**
- **Exports results** to a `.txt` file for later review
- **Customizable filters** for advanced targeting

---

## 🧠 How It Works

The bot automates your LinkedIn job search by:
1. Searching for job listings based on your filters  
2. Automatically submitting applications using your CV  
3. Logging results and details for later reference  
4. Optionally following the company after each successful submission  

---

## 🖥️ Supported Platforms

| Browser | macOS | Windows | Linux (Ubuntu) | Notes |
|:--------:|:------:|:--------:|:---------------:|:------|
| Chrome   | ✅ | ✅ | ✅ | Recommended browser |

---

## 🔐 Notes

- Your credentials and API key remain **local and private** — nothing is stored remotely.  
- Use responsibly and in compliance with **LinkedIn’s Terms of Service**.  
- This project is intended for **educational and personal use only**.  

---

## 💬 Contributing

Contributions, feature suggestions, and pull requests are welcome!  
If you encounter issues or have ideas for improvement, feel free to open an issue.

---

## 📜 License

Licensed under the **MIT License** — free for personal and commercial use with attribution.
