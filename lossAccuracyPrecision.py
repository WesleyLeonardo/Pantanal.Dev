from transformers import BertTokenizer, BertForSequenceClassification, AdamW
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, precision_score

import treinos
from transformers import BertTokenizer, BertForSequenceClassification
import torch

tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
model = BertForSequenceClassification.from_pretrained('bert-base-multilingual-cased')

def criar_dataset_manual(exemplos):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    input_ids = []
    attention_masks = []
    labels = []

    for exemplo in exemplos:
        texto = exemplo['texto']
        sentimento = exemplo['sentimento']

        encoding = tokenizer.encode_plus(
            texto,
            add_special_tokens=True,
            max_length=512,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        input_ids.append(encoding['input_ids'].squeeze())
        attention_masks.append(encoding['attention_mask'].squeeze())
        labels.append(sentimento)

    dataset = torch.utils.data.TensorDataset(
        torch.stack(input_ids),
        torch.stack(attention_masks),
        torch.tensor(labels)
    )

    return dataset

dataset_treinamento = criar_dataset_manual(treinos.exemplos_treinamento)

batch_size = 16
epochs = 5
learning_rate = 2e-5
        
train_loader = DataLoader(dataset_treinamento, batch_size=batch_size, shuffle=True)
    
test_loader = DataLoader(dataset_treinamento, batch_size=batch_size, shuffle=False)

        
optimizer = AdamW(model.parameters(), lr=learning_rate)
loss_fn = torch.nn.CrossEntropyLoss()
    
def test(model, dataloader):
    model.eval()
    predictions = []
    labels = []

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch[0].to(device)
            attention_mask = batch[1].to(device)
            true_labels = batch[2].to(device)

            outputs = model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            predicted_labels = torch.argmax(logits, dim=1)

            predictions.extend(predicted_labels.tolist())
            labels.extend(true_labels.tolist())
    accuracy = accuracy_score(labels, predictions)
    precision = precision_score(labels, predictions, average='weighted')
    return accuracy, precision
        
    
def train(model, dataloader, optimizer, loss_fn):
    model.train()
    total_loss = 0.0
            
    for batch in dataloader:
        optimizer.zero_grad()
        input_ids = batch[0].to(device)
        attention_mask = batch[1].to(device)
        labels = batch[2].to(device)
                
        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        total_loss += loss.item()
                
        loss.backward()
        optimizer.step()
                
    avg_loss = total_loss / len(dataloader)
    return avg_loss
        
def main():
    for epoch in range(epochs):
        loss = train(model, train_loader, optimizer, loss_fn)
        print(f'Epoch {epoch+1}/{epochs}, Loss: {loss}')
            
        accuracy, precision = test(model, test_loader)
        print(f'Epoch {epoch+1}/{epochs}, Accuracy: {accuracy}, Precision: {precision}')
    
if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    main()
