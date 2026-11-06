"""Validate a canonical KnowledgeResponse file; report external relations."""
import argparse
from pathlib import Path
from card_models import KnowledgeResponse

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    bundle = KnowledgeResponse.model_validate_json(args.input.read_text())
    ids = {c.card_id for c in bundle.cards}
    external = sorted({r.target_card_id for c in bundle.cards for r in c.relations if r.target_card_id not in ids})
    print(f'Valid: {len(bundle.cards)} cards')
    if external:
        print('External relation targets (not verified locally): ' + ', '.join(external))

if __name__ == '__main__':
    main()
