# Unavailable This Week Feature

This guide explains how to mark participants as unavailable for a specific week.

## When to Use This

Use the `unavailable_this_week` feature when someone:
- Is on vacation
- Is sick
- Can't participate this week for any reason

## How It Works

### Step 1: Edit config.yaml

Open `config/config.yaml` and find the `unavailable_this_week` field:

```yaml
rotation:
  participants:
    - "Jack"
    - "Joe"
    - "Eldon"
    - "Sean"
    - "Jin"

  # Add names of people unavailable THIS WEEK
  unavailable_this_week: ["Sean"]
```

### Step 2: Generate Message

Run the bot as usual:

```bash
python -m src.bot_simple
```

### Step 3: Next Week - Reset It

**Important**: Remember to clear the list for next week!

```yaml
unavailable_this_week: []
```

---

## Examples

### Example 1: One Person Unavailable (5 → 4 people)

**Config:**
```yaml
participants: ["Jack", "Joe", "Eldon", "Sean", "Jin"]
unavailable_this_week: ["Sean"]
```

**Output:**
```
📅 Week 1 - All Together!

👥 Team: Jack, Joe, Eldon, Jin

Have a great week!

⚠️ Unavailable this week: Sean
```

Note: With 4 people (< 5), everyone stays in one group!

---

### Example 2: Multiple People Unavailable (5 → 3 people)

**Config:**
```yaml
participants: ["Jack", "Joe", "Eldon", "Sean", "Jin"]
unavailable_this_week: ["Sean", "Jin"]
```

**Output:**
```
📅 Week 1 - All Together!

👥 Team: Jack, Joe, Eldon

Have a great week!

⚠️ Unavailable this week: Sean, Jin
```

---

### Example 3: No One Unavailable (Normal Week)

**Config:**
```yaml
participants: ["Jack", "Joe", "Eldon", "Sean", "Jin"]
unavailable_this_week: []
```

**Output:**
```
📅 Week 1 Rotation

🏢 Main Group: Joe, Eldon, Sean, Jin
🌟 Solo: Jack

Have a great week!
```

---

## How It Affects Rotation

### Normal Rotation (5 people)
- **Week 1**: Jack solo, others main
- **Week 2**: Joe solo, others main
- **Week 3**: Eldon solo, others main
- **Week 4**: Sean solo, others main
- **Week 5**: Jin solo, others main

### With Someone Unavailable

If Sean is unavailable on Week 4:
- **Week 4**: Only 4 people available → Everyone in one group
- **Week 5**: Back to normal → Jin solo (rotation continues)

**Important**: The rotation counter keeps going! Even if someone is unavailable, the week number still increases. This ensures the rotation stays consistent.

---

## Tips

### Weekly Workflow

1. **Monday morning**: Check who's available
2. **Edit config.yaml**: Add unavailable people if needed
3. **Run bot**: `python -m src.bot_simple`
4. **Copy message**: Paste into Instagram
5. **Next week**: Remember to clear `unavailable_this_week: []`

### Quick Edit Shortcut

You can edit just the unavailable line without opening the whole file:

```bash
# Mark Sean as unavailable
sed -i '' 's/unavailable_this_week: \[\]/unavailable_this_week: ["Sean"]/' config/config.yaml

# Reset for next week
sed -i '' 's/unavailable_this_week: .*/unavailable_this_week: []/' config/config.yaml
```

### Multiple People

Separate names with commas:

```yaml
unavailable_this_week: ["Jack", "Joe", "Sean"]
```

### Case Sensitive

Names must match exactly:
- ✅ `["Jack"]` - Correct
- ❌ `["jack"]` - Won't match
- ❌ `["JACK"]` - Won't match

---

## Troubleshooting

### "No participants available this week"

**Problem**: All participants marked as unavailable

**Solution**: At least one person must be available

---

### Person still shows up in rotation

**Problem**: Name doesn't match exactly

**Solution**: Check spelling and capitalization in config.yaml:
```yaml
participants:
  - "Jack"  # Exact name here

unavailable_this_week: ["Jack"]  # Must match exactly
```

---

### Forgot to reset last week

**Problem**: Someone marked unavailable from last week

**Solution**: Just edit config.yaml and set back to `[]`

---

## GitHub Actions

If using GitHub Actions, you'll need to edit the config file and push:

```bash
# Edit config.yaml to mark someone unavailable
vim config/config.yaml

# Commit and push
git add config/config.yaml
git commit -m "Mark Sean as unavailable this week"
git push

# Next week, reset and push again
git add config/config.yaml
git commit -m "Reset unavailable list"
git push
```

---

## Summary

✅ **Easy to use**: Just add names to a list
✅ **Temporary**: Only affects current week
✅ **Flexible**: Works with single person or multiple people
✅ **Clear**: Shows who's unavailable in the message
⚠️ **Remember**: Reset the list each week!

---

That's it! Simple way to handle vacations and absences. 🌴
