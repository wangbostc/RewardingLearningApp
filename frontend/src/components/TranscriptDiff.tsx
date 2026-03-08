interface SpeechTokenFeedback {
  text: string;
  status: 'correct' | 'wrong' | 'missing' | 'extra' | 'neutral';
}

interface TranscriptDiffProps {
  title: string;
  tokens: SpeechTokenFeedback[];
  counterpartTokens?: SpeechTokenFeedback[];
  emptyText?: string;
}

const punctuationRegex = /^[.,!?;:'")\]]+$/;

function tokenClassName(status: SpeechTokenFeedback['status']) {
  switch (status) {
    case 'correct':
      return 'bg-green-100 text-green-800';
    case 'missing':
      return 'bg-amber-100 text-amber-900 ring-1 ring-amber-300 line-through';
    case 'wrong':
      return 'bg-red-100 text-red-800 ring-1 ring-red-200';
    case 'extra':
      return 'bg-purple-100 text-purple-800 ring-1 ring-purple-200';
    default:
      return 'text-gray-700';
  }
}

function buildDifferenceMask(source: string, target: string) {
  const a = Array.from(source);
  const b = Array.from(target);
  const dp = Array.from({ length: a.length + 1 }, () => Array(b.length + 1).fill(0));

  for (let i = a.length - 1; i >= 0; i -= 1) {
    for (let j = b.length - 1; j >= 0; j -= 1) {
      if (a[i].toLowerCase() === b[j].toLowerCase()) {
        dp[i][j] = dp[i + 1][j + 1] + 1;
      } else {
        dp[i][j] = Math.max(dp[i + 1][j], dp[i][j + 1]);
      }
    }
  }

  const commonMask = Array(a.length).fill(false);
  let i = 0;
  let j = 0;

  while (i < a.length && j < b.length) {
    if (a[i].toLowerCase() === b[j].toLowerCase()) {
      commonMask[i] = true;
      i += 1;
      j += 1;
    } else if (dp[i + 1][j] >= dp[i][j + 1]) {
      i += 1;
    } else {
      j += 1;
    }
  }

  return commonMask.map((isCommon) => !isCommon);
}

function renderTokenText(token: SpeechTokenFeedback, counterpartText?: string) {
  if (token.status !== 'wrong' || !counterpartText) {
    return token.text;
  }

  const diffMask = buildDifferenceMask(token.text, counterpartText);

  return Array.from(token.text).map((character, index) => (
    <span
      key={`${character}-${index}`}
      className={diffMask[index] ? 'font-bold underline decoration-2 underline-offset-2' : ''}
    >
      {character}
    </span>
  ));
}

export default function TranscriptDiff({
  title,
  tokens,
  counterpartTokens = [],
  emptyText = 'No words captured yet.',
}: TranscriptDiffProps) {
  const hasWords = tokens.some((token) => /\w/.test(token.text));
  const counterpartWrongTokens = counterpartTokens
    .filter((token) => token.status === 'wrong')
    .map((token) => token.text);
  let wrongTokenIndex = 0;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-sm font-semibold text-gray-600">{title}</h3>
      {hasWords ? (
        <div className="text-lg leading-9 text-gray-900">
          {tokens.map((token, index) => {
            const isPunctuation = punctuationRegex.test(token.text);
            const counterpartText =
              token.status === 'wrong' ? counterpartWrongTokens[wrongTokenIndex++] : undefined;

            return (
              <span
                key={`${token.text}-${index}`}
                className={`inline-block rounded px-1 py-0.5 ${tokenClassName(token.status)} ${
                  isPunctuation ? 'mr-0' : 'mr-1'
                }`}
              >
                {renderTokenText(token, counterpartText)}
              </span>
            );
          })}
        </div>
      ) : (
        <p className="text-sm text-gray-500">{emptyText}</p>
      )}
    </div>
  );
}
