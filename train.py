import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
from tqdm import tqdm
from dataset import create_data_loaders
from emotion_analyzer import EmotionClassifier, EMOTIONS

def train_improved():
    """
    개선된 학습 (BERT 일부 학습)
    """
    print("=" * 60)
    print("개선된 학습 (BERT 마지막 레이어 학습)")
    print("=" * 60)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n✓ 디바이스: {device}")
    
    # 데이터 로더
    train_loader, val_loader, test_loader = create_data_loaders(batch_size=16)
    
    # 모델
    print("\n모델 초기화 중...")
    model = EmotionClassifier(num_classes=6).to(device)
    
    # BERT 마지막 2개 레이어만 학습
    for name, param in model.bert.named_parameters():
        if 'encoder.layer.10' in name or 'encoder.layer.11' in name or 'pooler' in name:
            param.requires_grad = True
        else:
            param.requires_grad = False
    
    # Classifier는 학습
    for param in model.classifier.parameters():
        param.requires_grad = True
    
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"✓ BERT 마지막 2개 레이어 + Classifier 학습")
    print(f"✓ 학습 파라미터: {trainable:,}개")
    
    # 옵티마이저 (서로 다른 학습률)
    optimizer = AdamW([
        {'params': [p for n, p in model.bert.named_parameters() if p.requires_grad], 
         'lr': 2e-5},  # BERT는 천천히
        {'params': model.classifier.parameters(), 
         'lr': 5e-4}   # Classifier는 빠르게
    ], weight_decay=0.01)
    
    # 스케줄러
    scheduler = CosineAnnealingWarmRestarts(optimizer, T_0=3, T_mult=2)
    
    criterion = nn.CrossEntropyLoss()
    
    print(f"\n학습 시작 (최대 30 에포크)")
    print("=" * 60)
    
    best_val_acc = 0
    patience = 0
    max_patience = 7
    
    for epoch in range(1, 31):
        # 학습
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0
        
        for batch in tqdm(train_loader, desc=f'Epoch {epoch:2d}'):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            optimizer.zero_grad()
            outputs = model(input_ids, attention_mask)
            loss = criterion(outputs, labels)
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            
            train_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            train_correct += (preds == labels).sum().item()
            train_total += labels.size(0)
        
        # 검증
        model.eval()
        val_loss = 0
        val_correct = 0
        val_total = 0
        
        emotion_correct = [0] * 6
        emotion_total = [0] * 6
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['label'].to(device)
                
                outputs = model(input_ids, attention_mask)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)
                
                for i in range(len(labels)):
                    label = labels[i].item()
                    emotion_total[label] += 1
                    if preds[i] == labels[i]:
                        emotion_correct[label] += 1
        
        train_loss /= len(train_loader)
        val_loss /= len(val_loader)
        train_acc = train_correct / train_total
        val_acc = val_correct / val_total
        
        print(f"\nEpoch {epoch}:")
        print(f"  학습   - Loss: {train_loss:.4f}, Acc: {train_acc:.4f}")
        print(f"  검증   - Loss: {val_loss:.4f}, Acc: {val_acc:.4f}")
        
        # 감정별 정확도
        print(f"  감정별:")
        for i, emotion in enumerate(EMOTIONS):
            if emotion_total[i] > 0:
                acc = emotion_correct[i] / emotion_total[i]
                print(f"    {emotion:6s}: {acc:.4f}")
        
        # 학습률 조정
        scheduler.step()
        
        # 최고 모델 저장
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), 'emotion_model_best.pth')
            print(f"  ✨ 최고 모델 저장! (Acc: {val_acc:.4f})")
            patience = 0
        else:
            patience += 1
            print(f"  ⏳ 개선 없음 ({patience}/{max_patience})")
        
        # 조기 종료
        if patience >= max_patience:
            print(f"\n조기 종료 (Epoch {epoch})")
            break
    
    # 테스트
    print("\n" + "=" * 60)
    print("최종 테스트")
    print("=" * 60)
    
    model.load_state_dict(torch.load('emotion_model_best.pth'))
    model.eval()
    
    test_correct = 0
    test_total = 0
    
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            outputs = model(input_ids, attention_mask)
            _, preds = torch.max(outputs, 1)
            test_correct += (preds == labels).sum().item()
            test_total += labels.size(0)
    
    test_acc = test_correct / test_total
    
    print(f"\n✅ 테스트 정확도: {test_acc:.4f}")
    print(f"✅ 최고 검증 정확도: {best_val_acc:.4f}")
    print("=" * 60)

if __name__ == "__main__":
    train_improved()
