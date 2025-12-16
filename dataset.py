import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from kobert_transformers import get_tokenizer

class EmotionDataset(Dataset):
    """
    감정 분류 데이터셋 (6가지 감정)
    """
    def __init__(self, csv_file, max_length=128):
        self.data = pd.read_csv(csv_file)
        self.tokenizer = get_tokenizer()
        self.max_length = max_length
        
        print(f"  ✓ {csv_file} 로드 완료: {len(self.data):,}개")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        text = str(self.data.iloc[idx]['text'])
        emotion = int(self.data.iloc[idx]['emotion'])
        
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(emotion, dtype=torch.long)
        }


def create_data_loaders(batch_size=16):
    """
    학습/검증/테스트 데이터 로더 생성
    """
    print("\n데이터 로더 생성 중...")
    
    train_dataset = EmotionDataset('data/train.csv')
    val_dataset = EmotionDataset('data/val.csv')
    test_dataset = EmotionDataset('data/test.csv')
    
    train_loader = DataLoader(
        train_dataset, 
        batch_size=batch_size, 
        shuffle=True
    )
    
    val_loader = DataLoader(
        val_dataset, 
        batch_size=batch_size, 
        shuffle=False
    )
    
    test_loader = DataLoader(
        test_dataset, 
        batch_size=batch_size, 
        shuffle=False
    )
    
    print(f"✓ 학습 배치: {len(train_loader):,}개")
    print(f"✓ 검증 배치: {len(val_loader):,}개")
    print(f"✓ 테스트 배치: {len(test_loader):,}개")
    
    return train_loader, val_loader, test_loader


if __name__ == "__main__":
    print("=" * 60)
    print("데이터 로더 테스트")
    print("=" * 60)
    
    train_loader, val_loader, test_loader = create_data_loaders(batch_size=4)
    
    batch = next(iter(train_loader))
    
    print(f"\n📦 배치 정보:")
    print(f"  - Input IDs shape: {batch['input_ids'].shape}")
    print(f"  - Attention mask shape: {batch['attention_mask'].shape}")
    print(f"  - Labels shape: {batch['label'].shape}")
    print(f"  - Labels: {batch['label'].tolist()}")
    
    print("\n✓ 데이터 로더 정상 작동!")
