# 📊 Conclusion

## Missing Values 🛠️ 
Looking at the data, it seems that the categories with the most missing values are primarily related to product dimensions. Moving forward, we should aim to fill these missing values. This could be done using k-means clustering or other methods. I also acknowledge that some products may inherently lack certain dimension values due to their shape or size, but this should be specified and well-documented.

## Correlations 🔗 
Examining a correlation heatmap between product dimensions, we see there is very little to no correlation between them. The only relatively higher correlation is between product depth and volume.

## Quick Stats of Products by Department 📈 
From the product dimensions bar plot, a few interesting observations were made:

- **Weight**: Pets and Alcohol departments had the heaviest products on average.
- **Height and Volume**: Lifestyle department products were tallest and had the highest volume.
- **Number of Products**: Snacks and Personal Care departments had the most products.

The top 10 most purchased products were part of the Produce department, indicating that most purchases are for produce items.

## Looking at Changes Over Time ⏳
We only have data for a few weeks from the end of March to mid-April of 2020. During this period, there was a sharp increase in product purchases starting in early April, peaking at about 3700 products bought on April 6. After that, the trend sharply declines, suggesting that most products are purchased at the beginning of the month.

Products in each department follow a similar trend, with food-related purchases (e.g., Produce, Dairy and Eggs, Pantry) showing more significant fluctuations, while other departments exhibit a flatter trend. Examining purchases by the hour, we see that most are made around midday. The most popular products bought at each hour are from the Produce department, while the least bought products vary across departments.

## Comments on Modeling Tool 🤖
I used a variety of models to run predictions on purchases for a specific product. The best performers were Random Forest, XGBoost, and Decision Tree. Other models such as Support Vector Regression, Linear Regression, Lasso, and Ridge Regression did not perform as well, highlighting the importance of models that fit nonlinear data better than linear models. In the future, I would like to test how a neural network performs. Once the best models are identified, I plan to conduct additional feature engineering and hyperparameter tuning to build an accurate prediction tool.

## Next Steps 🚀 
From the data analysis, we can find ways to better handle product fulfillment based on the time of day and month. Using the prediction tool, we could implement better systems to manage future orders and be better prepared. By analyzing dimensions and product information for each department, we could further customize processes to improve operations. Much more analysis and model tuning is needed, but there are many areas to optimize and develop.

## Thank you for checking out my project. I would be happy to answer any questions about how I built it, my thought process, future steps, and feedback. I had a lot of fun doing this and am excited to see how I can further contribute. I look forward to the next steps! 🎉
