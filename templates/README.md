# 🤖 Agent Templates Directory

This directory contains everything you need to create custom agents for the multi-agent system quickly and easily.

## 📁 Files Overview

### 🎯 **Core Template Files**
- **`sample_agent_template.py`** - Complete template with all placeholders for creating custom agents
- **`weather_agent_example.py`** - Fully implemented example showing how to use the template
- **`create_agent.py`** - Interactive wizard script for automated agent generation

### 📚 **Documentation**
- **`AGENT_CREATION_GUIDE.md`** - Comprehensive guide for creating agents step-by-step
- **`README.md`** - This file - overview of the templates system

---

## 🚀 Quick Start

### Option 1: Interactive Wizard (Recommended)
```bash
# Run the interactive agent creation wizard
python templates/create_agent.py
```

The wizard will:
- ✅ Guide you through all necessary information
- ✅ Generate a complete agent file automatically  
- ✅ Create test scripts and configuration entries
- ✅ Provide next-step instructions

### Option 2: Manual Template Copy
```bash
# Copy the template and customize manually
cp templates/sample_agent_template.py agents/your_new_agent.py
```

Then replace all `[PLACEHOLDER]` values with your specific information.

---

## 📖 What You'll Create

Using these templates, you can create agents for any domain:

### 🌤️ **Weather Analysis Agent**
- Keywords: `weather`, `temperature`, `forecast`, `climate`
- Capabilities: Weather forecasting, climate analysis, alerts
- Example: Complete implementation in `weather_agent_example.py`

### 🍳 **Recipe Recommendation Agent**  
- Keywords: `recipe`, `cooking`, `ingredients`, `food`
- Capabilities: Recipe search, nutrition analysis, meal planning
- Perfect for culinary applications

### 📈 **Stock Analysis Agent**
- Keywords: `stock`, `investment`, `market`, `portfolio`
- Capabilities: Market analysis, portfolio optimization, risk assessment
- Great for financial applications

### 🎵 **Music Recommendation Agent**
- Keywords: `music`, `song`, `artist`, `playlist`
- Capabilities: Music discovery, playlist generation, artist analysis
- Ideal for entertainment applications

---

## ✅ Template Features

### 🔧 **Built-in Functionality**
- ✅ **Democratic Agent Selection** - Automatic relevance scoring
- ✅ **Memory Integration** - STM and LTM storage and retrieval
- ✅ **Context Awareness** - Historical query context
- ✅ **Error Handling** - Robust error management
- ✅ **Logging** - Comprehensive activity logging

### 🎯 **Customizable Components**
- ✅ **Domain Keywords** - Define what triggers your agent
- ✅ **Capabilities** - Specify what your agent can do
- ✅ **Confidence Scoring** - Fine-tune query matching
- ✅ **Custom Methods** - Implement domain-specific logic
- ✅ **Categories & Focus** - Organize your agent's expertise

### 🔗 **System Integration**
- ✅ **Multi-Agent Collaboration** - Works with existing agents
- ✅ **Edge Connections** - Define communication paths
- ✅ **Configuration Ready** - JSON config generation
- ✅ **Testing Framework** - Auto-generated test scripts

---

## 📋 Requirements Checklist

Before creating an agent, ensure you have:

- [ ] **Domain Expertise** - Knowledge of your target area
- [ ] **Python Basics** - Understanding of Python programming
- [ ] **Clear Use Cases** - Specific problems your agent will solve
- [ ] **Keywords List** - Terms users would search for
- [ ] **Capabilities Definition** - What your agent can do

---

## 🎯 Creation Process

### 1. **Planning Phase**
- Define your agent's domain and purpose
- List keywords users would search for
- Identify capabilities and expertise areas
- Plan integration with existing agents

### 2. **Generation Phase**
- Run `python templates/create_agent.py` (recommended)
- OR copy and customize `sample_agent_template.py` manually
- Implement custom domain-specific methods

### 3. **Integration Phase**
- Add agent to `core/agents.json`
- Define edge connections with other agents
- Test agent in isolation
- Test multi-agent scenarios

### 4. **Deployment Phase**
- Restart FastAPI server
- Monitor agent performance
- Adjust confidence scoring as needed
- Gather user feedback for improvements

---

## 🛠️ Customization Tips

### **Keywords Selection**
Choose keywords that users naturally use when asking about your domain:
```python
# Good keywords - natural user language
["weather", "temperature", "forecast", "rainy", "sunny"]

# Avoid - too technical
["meteorological_analysis", "barometric_pressure"]
```

### **Capabilities Design**
Define specific, actionable capabilities:
```python
# Good capabilities - specific and actionable
["recipe_search", "nutrition_analysis", "meal_planning"]

# Avoid - too vague
["food_stuff", "cooking_things"]
```

### **Confidence Tuning**
Start conservative and adjust based on performance:
```python
# Conservative approach - prevents false positives
if "exact_match" in query: confidence += 0.4
if "related_term" in query: confidence += 0.2
```

---

## 📊 Template Structure

```
templates/
├── sample_agent_template.py     # Main template file
├── weather_agent_example.py     # Complete working example  
├── create_agent.py              # Interactive creation wizard
├── AGENT_CREATION_GUIDE.md      # Detailed documentation
└── README.md                    # This overview file
```

---

## 🤝 Support

### **Getting Help**
1. **Read the Guide**: Check `AGENT_CREATION_GUIDE.md` for detailed instructions
2. **Study Examples**: Review `weather_agent_example.py` for implementation patterns
3. **Test Incrementally**: Start simple and add complexity gradually
4. **Check Existing Agents**: Look at `agents/` directory for more examples

### **Common Issues**
- **Agent not triggered**: Check keyword relevance and confidence scoring
- **Errors in processing**: Verify all template placeholders are replaced
- **Memory issues**: Ensure memory manager is properly initialized
- **Multi-agent conflicts**: Review edge connections and priorities

---

## 🎉 Success Stories

With these templates, you can create agents for virtually any domain:

- **Educational Agents**: Tutoring, course recommendations, learning paths
- **Health Agents**: Symptom analysis, wellness tips, exercise planning  
- **Business Agents**: Market research, competitor analysis, strategy planning
- **Creative Agents**: Writing assistance, design suggestions, creative inspiration
- **Technical Agents**: Code review, architecture advice, debugging help

**The possibilities are endless! 🚀**

---

**Ready to create your first agent? Run `python templates/create_agent.py` and let the wizard guide you!**
