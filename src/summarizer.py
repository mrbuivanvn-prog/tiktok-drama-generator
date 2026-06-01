"""
News summarizer module for TikTok Drama Generator.
Generates short Vietnamese news scripts from headlines.
"""


def summarize_headline(headline: str) -> str:
    """Generate a short script from a headline."""
    h = headline.strip()
    lower = h.lower()

    if any(k in lower for k in ['chung kết', 'tranh cai', 'gay sốt', 'hot', 'trend', 'viral']):
        return (
            f"{h}. "
            "Đây là một trong những chủ đề đang được cộng đồng mạng xã hội quan tâm nhất hôm nay. "
            "Nhiều người cho rằng vấn đề này còn tiếp tục gây tranh cãi trong những ngày tới."
        )

    if any(k in lower for k in ['tuyển sinh', 'thi cử', 'lớp 10', 'đh', 'đại học']):
        return (
            f"{h}. "
            "Thông tin này ảnh hưởng trực tiếp đến học sinh và phụ huynh trên cả nước. "
            "Nhiều người đang theo dõi sát sao để có những chuẩn bị tốt nhất."
        )

    if any(k in lower for k in ['luong', 'giao viên', 'lương', 'từ 1/7', 'từ ngày']):
        return (
            f"{h}. "
            "Đây là thông tin liên quan đến đời sống và quyền lợi của người lao động. "
            "Dư luận đang có nhiều ý kiến trái chiều trước quyết định này."
        )

    if any(k in lower for k in ['trump', 'mỹ', 'hoa kỳ']):
        return (
            f"{h}. "
            "Diễn biến này cũng đang được giới phân tích theo dõi vì có thể ảnh hưởng đến bối cảnh khu vực. "
            "Cư dân mạng chia sẻ thông tin với tốc độ rất nhanh."
        )

    if any(k in lower for k in ['bóng đá', 'champions', 'world cup', 'tuyển']):
        return (
            f"{h}. "
            "Bóng đá luôn là chủ đề nóng trên mạng xã hội, đặc biệt vào cuối tuần. "
            "Các fan đang bàn tán sôi nổi về khả năng và diễn biến sắp tới."
        )

    if any(k in lower for k in ['sách', 'bán chạy', 'văn hóa']):
        return (
            f"{h}. "
            "Xu hướng này cho thấy người dân vẫn rất quan tâm đến văn hóa đọc. "
            "Nhiều bình luận cho rằng đây là tín hiệu tích cực cho cộng đồng."
        )

    if any(k in lower for k in ['sao', 'diễn viên', 'ca sĩ', 'nghệ sĩ']):
        return (
            f"{h}. "
            "Chủ đề này nhanh chóng lọt vào trending nhờ lượt tương tác cao từ cư dân mạng. "
            "Nhiều người đang chờ thêm những thông tin tiếp theo liên quan."
        )

    if any(k in lower for k in ['xã', 'phường', 'tp.hcm', 'hà nội', 'giao thông']):
        return (
            f"{h}. "
            "Thông tin địa phương này nhanh chóng thu hút sự chú ý vì liên quan đến đời sống hàng ngày. "
            "Người dân đang chia sẻ và thảo luận rất sôi nổi."
        )

    return (
        f"{h}. "
        "Đây là một trong những chủ đề đang thu hút sự chú ý của cộng đồng mạng. "
        "Nhiều người đang bàn tán và chia sẻ thông tin liên quan."
    )


def build_script(trends):
    """Build a list of script lines from trend items."""
    results = []
    for trend in trends:
        topic = getattr(trend, 'topic', str(trend))
        results.append({
            'headline': topic,
            'script': summarize_headline(topic),
            'source': getattr(trend, 'source', ''),
        })
    return results
