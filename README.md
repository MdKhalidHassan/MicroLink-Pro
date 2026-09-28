# 🎙️ MicroLink Pro

**MicroLink** একটি সহজ এবং হালকা GUI টুল, যার মাধ্যমে আপনি আপনার অ্যান্ড্রয়েড ফোনকে সরাসরি লিনাক্স (Ubuntu) পিসির **Virtual Microphone** হিসেবে ব্যবহার করতে পারবেন। এটি দিয়ে গুগল জেমিনি (Gemini), গুগল ড্রাইভ, ওয়েব ব্রাউজার কিংবা যেকোনো সাউন্ড রেকর্ডারে ফোনের ব্যাকগ্রাউন্ড মাইক দিয়ে ভয়েস টাইপিং করতে পারবেন।

---

## ⚡ ১. দ্রুত সেটআপ (Quick One-Line Installation)

নতুনদের সুবিধার্থে সমস্ত ডিটেন্ডেন্সি এবং সিস্টেম ডিপেন্ডেন্সি ইনস্টল করার জন্য টার্মিনালে শুধু এই একক কমান্ডটি রান করুন:

```bash
sudo apt update && sudo apt install -y python3 python3-tk android-tools-adb scrcpy pulseaudio-utils

📱 ২. ফোনের সেটিংস (Phone Configuration)
১. আপনার অ্যান্ড্রয়েড ফোনের Settings > About Phone-এ যান।
২. Build Number-এর ওপর পরপর ৭ বার ট্যাপ করে Developer Options চালু করুন।
৩. Developer Options-এ ঢুকে USB Debugging অপশনটি অন (Enable) করে দিন।
৪. ইউএসবি ক্যাবল দিয়ে ফোনটিকে পিসির সাথে যুক্ত করুন।
৫. ফোনের স্ক্রিনে "Allow USB Debugging?" পপ-আপ আসলে Always allow বক্সে টিক দিয়ে Allow নির্বাচন করুন।

🚀 ৩. সফটওয়্যার চালনা (How to Run)
১. প্রজেক্টের ফোল্ডারে টার্মিনাল খুলুন।
২. নিচের কমান্ডটি দিয়ে অ্যাপ্লিকেশনটি চালু করুন:

Bash
python3 main.py
🎙️ ৪. জেমিনি / ব্রাউজারে ভয়েস টাইপিংয়ের নিয়ম (How to Use)
১. অ্যাপটি চালু হলে এটি স্বয়ংক্রিয়ভাবে আপনার ফোন ডিটেক্ট করবে।
২. 🎙️ Start Virtual Microphone বাটনে ক্লিক করুন।
৩. আপনার লিনাক্সের Settings > Sound > Input অপশনে গিয়ে MicroLinkInput ডিভাইসটি সিলেক্ট করুন।
৪. এখন গুগল ক্রোম বা ব্রাউজারে জেমিনি (Gemini) খুলে মাইক আইকনে চাপ দিন এবং ফোনে কথা বলা শুরু করুন!

🛑 ৫. মাইক বন্ধ করা (Stop Engine)
কাজ শেষ হলে অ্যাপের 🛑 Stop Virtual Microphone বাটনে ক্লিক করুন। এতে ভার্চুয়াল সিস্টেম মাইকটি আনলোড হয়ে পিসি আগের স্বাভাবিক অবস্থায় ফিরে যাবে।

⚠️ সাধারণ সমস্যা ও সমাধান (Troubleshooting)
ADB/Phone not detected?
ইউএসবি ক্যাবল পরিবর্তন করে দেখুন অথবা ফোনে USB Connection Mode নির্বাচন করে Transfer Files (MTP) মুড সেট করুন।

Permission Denied?
টার্মিনালে adb kill-server && adb start-server রান করে আবার ইউএসবি প্লাগ-ইন করুন।


<ElicitationsGroup message="পরবর্তী পদক্ষেপে কী করতে চান?">
  <Elicitation label="গিটহাব রিপোজিটরি খোলার জন্য .gitignore ফাইল তৈরি করুন" query="MicroLink প্রজেক্টের জন্য একটি উপযুক্ত .gitignore ফাইল তৈরি করে দাও।"/>
  <Elicitation label="প্রজেক্টটি ডেস্কটপ শর্টকাট (App Launcher) হিসেবে যোগ করার উপায় জানুন" query="MicroLink অ্যাপের জন্য উবুন্টুতে একটি .desktop ফাইল বা ডেস্কটপ শর্টকাট তৈরি করার কোড দাও।"/>
</ElicitationsGroup>
